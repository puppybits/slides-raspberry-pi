from bottle import *
from ofxclient import Institution

app = Bottle(__name__)

@app.post('/transactions')
def download()
    params = json.loads(request.params.dict.keys()[0])
    account = params['account']
    password = params['password']
    days = params['days']
    
    inst = Institution(
            id = '54324',
            org = 'America First Credit Union',
            url = 'https://ofx.americafirst.com',
            username = '',
            password = ''
    )
    
    accounts = inst.accounts()[0]
    download  = a.download(days=days)
    
    return download
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug(mode=True)
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=port, reloader=True)
