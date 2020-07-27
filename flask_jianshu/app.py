import pymongo as pymongo
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def login():
    #加载用户信息
    client=pymongo.MongoClient('127.0.0.1')
    db=client['jianshu']
    ures=db['tabuser'].find({},{'_id':0})
    ulist=[u for u in ures]
    client.close()
    return render_template('ulogin.html',list=ulist)
def hello_world():
    #链接数据库
    client=pymongo.MongoClient('127.0.0.1')
    db = client['jianshu']
    tli = db['tabtimeline'].find({}, {'slug':1,'_id': 0})
    userlist = [i['slug'] for i in tli]
    x=[{
        'name':'牛肉','value':500},
        {'name':'牛肉','value':500},
        {'name':'牛肉','value':500},
    ]
    return render_template('index.html',)


if __name__ == '__main__':
    app.run()
