import asyncio, json
from playwright.async_api import async_playwright
import os
URL='file://'+os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'index.html')
CHECK = """()=>{
  const val=(d,a)=>a==='colour'?d.co:a==='species'||a==='shape'?d.sp:a==='size'?d.sz:a==='legs'?SPECIES[d.sp].legs:a==='horns'?SPECIES[d.sp].horns:a==='hair'?d.hair:d.glasses;
  const bad=[]; const seen={};
  for(let L=1;L<=400;L++) for(let rep=0;rep<12;rep++){
    const R=genRound(L); seen[R.attr]=(seen[R.attr]||0)+1; const v=val(R.example,R.attr);
    if(R.items.length!==R.n) bad.push(['count',L]);
    const m=R.items.filter(d=>d.match);
    if(m.length!==R.k||R.k<2||R.k>=R.n) bad.push(['k',L,m.length,R.k,R.n]);
    R.items.forEach(d=>{ const same=val(d,R.attr)===v; if(same!==d.match) bad.push(['mismatch',L,R.attr,JSON.stringify(d),v]);
      if(R.attr==='horns'&&SPECIES[d.sp].horns===null) bad.push(['hornnull',L]);
      if(v===null||v===undefined) bad.push(['nullv',L,R.attr]);
      if((R.attr==='species'||R.attr==='shape')&&!d.match&&SPECIES[R.example.sp].like.includes(d.sp)) bad.push(['lookalike',L]); });
    if(R.attr==='size'){ if(new Set(R.items.map(d=>d.sp)).size!==1) bad.push(['sizesp',L]); }
    if(R.n>12) bad.push(['n',L]);
  }
  return {bad:bad.slice(0,10),nbad:bad.length,seen};
}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, locale='en-US')
        pg = await ctx.new_page(); errs=[]
        pg.on('console', lambda m: errs.append(f'console.{m.type}: {m.text}') if m.type in('error','warning') else None)
        pg.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
        await pg.goto(URL); await pg.wait_for_selector('#title.on'); await pg.wait_for_timeout(1200)
        print('generator check', json.dumps(await pg.evaluate(CHECK)))
        print('spelling en-US ->', await pg.evaluate("W_COLOUR()"), '| speech', await pg.evaluate("speechLang()"))
        await pg.tap('#btnPlay', force=True)
        ads=0
        for lv in range(1,8):
            await pg.wait_for_function("!G.busy && $('#game').classList.contains('on')", timeout=15000)
            assert await pg.evaluate("G.round.level")==lv
            if lv==1: print('sentence:', await pg.inner_text('#sentence'))
            # one wrong tap then all right taps, with real touch events
            idx = await pg.evaluate("cells.map((c,i)=>[i,c.d.match])")
            wrong=[i for i,m in idx if not m][0]
            await pg.locator('.cell').nth(wrong).tap(force=True); await pg.wait_for_timeout(200)
            assert await pg.evaluate("G.wrong")==1 and await pg.evaluate("G.found")==0
            for i,m in idx:
                if m:
                    await pg.locator('.cell').nth(i).tap(force=True); await pg.wait_for_timeout(120)
                    await pg.locator('.cell').nth(i).tap(force=True)   # double tap must not double count
            if lv==2: await pg.wait_for_timeout(700); await pg.screenshot(path='/tmp/found.png')
            await pg.wait_for_selector('#party.on', timeout=8000)
            await pg.wait_for_function("$('#pbtns').classList.contains('show')", timeout=8000)
            if lv in (1,2): await pg.wait_for_timeout(600); await pg.screenshot(path=f'/tmp/party{lv}.png')
            vid = await pg.evaluate("(()=>{const v=$('#partyVid');return [v.style.display,v.paused,v.readyState,v.videoWidth]})()")
            stars = await pg.evaluate("document.querySelectorAll('#pstars .gold').length")
            await pg.tap('#btnNext', force=True); await pg.wait_for_timeout(400)
            ad = await pg.evaluate("$('#ad').classList.contains('on')")
            print(f'level {lv}: stars {stars}, video {vid}, ad after: {ad}')
            if ad:
                ads+=1; await pg.screenshot(path='/tmp/ad.png'); await pg.wait_for_selector('#ad.on', state='hidden', timeout=9000)
        print('ads shown in 7 levels:', ads, '| saved', await pg.evaluate("JSON.stringify(save)"))
        # home, grown-ups gate, purchase simulation
        await pg.wait_for_function("!G.busy"); await pg.tap('#btnHome', force=True); await pg.wait_for_selector('#title.on')
        await pg.screenshot(path='/tmp/title2.png')
        await pg.tap('#btnGrown'); await pg.wait_for_selector('#gate.on'); await pg.screenshot(path='/tmp/gate.png')
        for k in ['1','OK']: await pg.click(f'#gateKeys button[data-k="{k}"]')
        assert await pg.evaluate("$('#gate').classList.contains('on') && !$('#grown').classList.contains('on')"), 'gate let a wrong answer through'
        ans = str(await pg.evaluate("gateA"))
        for k in list(ans)+['OK']: await pg.click(f'#gateKeys button[data-k="{k}"]')
        await pg.wait_for_selector('#grown.on'); await pg.wait_for_timeout(400); await pg.screenshot(path='/tmp/grown.png')
        await pg.click('#btnBuy'); await pg.wait_for_selector('#confirm.on'); await pg.screenshot(path='/tmp/buy.png'); await pg.click('#cfYes'); await pg.wait_for_timeout(300)
        print('adFree after purchase:', await pg.evaluate("save.adFree"), '| buy button hidden:', await pg.evaluate("$('#btnBuy').style.display"))
        await pg.click('#grown .seg[data-k="spell"] button[data-v="uk"]'); print('spelling toggle ->', await pg.evaluate("W_COLOUR()"))
        await pg.click('#grownX')
        # no ads once purchased
        await pg.evaluate("save.sinceAd=3"); await pg.tap('#btnPlay', force=True)
        await pg.wait_for_function("!G.busy && $('#game').classList.contains('on')")
        await pg.evaluate("cells.filter(c=>c.d.match).forEach(c=>tapCell(c))"); await pg.wait_for_function("$('#pbtns').classList.contains('show')", timeout=9000)
        await pg.tap('#btnNext', force=True); await pg.wait_for_timeout(400)
        print('ad shown when adFree:', await pg.evaluate("$('#ad').classList.contains('on')"))
        # persistence across reload
        await pg.reload(); await pg.wait_for_selector('#title.on'); await pg.wait_for_function("!$('#app').classList.contains('pullback')"); print('after reload:', await pg.inner_text('#playLbl'), '| stars', await pg.inner_text('#starCount'))
        # rotate mid-round
        await pg.tap('#btnPlay', force=True); await pg.wait_for_function("!G.busy && $('#game').classList.contains('on')")
        await pg.set_viewport_size({'width':844,'height':390}); await pg.wait_for_timeout(500)
        ov = await pg.evaluate("(()=>{const f=$('#field').getBoundingClientRect();return cells.every(c=>{const r=c.el.getBoundingClientRect();return r.left>=f.left-1&&r.right<=f.right+1&&r.top>=f.top-1&&r.bottom<=f.bottom+1&&r.width>40})})()")
        print('cells inside field after rotate:', ov); await pg.screenshot(path='/tmp/rot.png')
        print('\n'.join(errs) or 'no console errors'); await b.close()
asyncio.run(main())
