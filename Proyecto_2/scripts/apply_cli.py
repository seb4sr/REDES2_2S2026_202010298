"""Apply saved IOS commands through Packet Tracer's actual CLI API."""
import asyncio, json, sys
from pathlib import Path
from build_project import OUT, call

async def main():
    paths=sorted((OUT/'configs').glob(sys.argv[1] if len(sys.argv)>1 and sys.argv[1]!='base' else '*.cfg'))
    if len(sys.argv)>1 and sys.argv[1]=='base':paths=[p for p in paths if '_ACL' not in p.stem]
    for path in paths:
        name=path.stem.split('_')[0]
        commands=[s for s in path.read_text(encoding='utf-8').splitlines() if s!='enable']
        js='var d=ipc.network().getDevice('+json.dumps(name)+');var out=[];var cl=d.getCommandLine();if(String(cl.getPrompt()).indexOf("[yes/no]")>=0){cl.enterCommand("no");}cl.enterCommand("");d.enterCommand("end","enable");'
        js+='var cmds='+json.dumps(commands)+';'
        js+='for(var i=0;i<cmds.length;i++){try{var r=d.enterCommand(cmds[i],"");out.push({command:cmds[i],result:r});}catch(e){out.push({command:cmds[i],error:String(e)});break;}}reportResult(JSON.stringify(out));'
        result=await call('pt_send_raw',dict(js_code=js,wait_result=True))
        (OUT/'evidencias'/(path.stem+'_cli.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        if any(s in str(result) for s in ['timeout','Sin respuesta','no hay canal','OFFLINE']):
            raise RuntimeError('CLI response missing; stopped without assuming success: '+name)

if __name__=='__main__': asyncio.run(main())
