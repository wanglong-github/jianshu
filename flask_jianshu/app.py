import pymongo as pymongo
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/',methods=['POST','GET'])
def login():
    if request.method=='GET':
        #加载用户信息
        client=pymongo.MongoClient('127.0.0.1')
        db=client['jianshu']
        ures=db['tabuser'].find({},{'_id':0})
        tli = db['tabtimeline'].find({}, {'slug': 1, '_id': 0})
        timeusers=[u for u in tli]
        ulist=[u for u in ures for x in timeusers if u['slug']==x['slug']]

        client.close()
        return render_template('ulogin.html',list=ulist)
    else:
        #接受slug
        user_slug=request.form['uid']
        return redirect(url_for('timeline',slug=user_slug))
@app.route('/tline')
def timeline():
    #获取用户id
    slug=request.args.get('slug')
    #链接数据库
    client=pymongo.MongoClient('127.0.0.1')
    db = client['jianshu']

    xli=db['tabtimeline'].find({'slug':slug},{'_id':0})
    # print([i for i in xli])
    #按照动态信息的类型进行汇总
    xtype=[{'name':'发表评论','value':0},
           {'name':'喜欢文章','value':0},
           {'name':'赞赏文章','value': 0},
           {'name':'发表文章','value': 0},
           {'name':'关注用户','value': 0},
           {'name':'关注专题','value': 0},
           {'name':'点赞评论','value': 0},
           {'name':'关注文集','value': 0},
    ]
    #统计发表文章信息
    dict_pub={}
    #得到动态信息
    for i in xli:
        #获取评论集合
        for it in i['dydata']:
            #判断字典是否有相关key，统计
            if 'comment_note' in it.keys():
                # print(f'发表评论:{len(it["comment_note"])}')
                #修改对应类型数量的储存
                for type in xtype:
                    if type['name']=='发表评论':
                        type['value']=len(it["comment_note"])
                        break
            elif 'like_note' in it.keys():
                for type in xtype:
                    if type['name']=='喜欢文章':
                        type['value']=len(it["like_note"])
                        break
            elif 'reward_note' in it.keys():
                for type in xtype:
                    if type['name']=='赞赏文章':
                        type['value']=len(it["reward_note"])
                        break

            elif 'share_note' in it.keys():
                #遍历发表文章
                for k in it ['share_note']:
                    mk=list(k.keys())[0][:7]
                    dict_pub.setdefault(mk,0)
                    dict_pub[mk]+=1
                for type in xtype:
                    if type['name']=='发表文章':
                        type['value']=len(it["share_note"])
                        break
            elif 'like_user' in it.keys():
                for type in xtype:
                    if type['name']=='关注用户':
                        type['value']=len(it["like_user"])
                        break
            elif 'like_collection' in it.keys():
                for type in xtype:
                    if type['name']=='关注专题':
                        type['value']=len(it["like_collection"])
                        break
            elif 'like_comment' in it.keys():
                for type in xtype:
                    if type['name']=='点赞评论':
                        type['value']=len(it["like_comment"])
                        break
            elif 'like_notebook' in it.keys():
                for type in xtype:
                    if type['name']=='关注文集':
                        type['value']=len(it["like_notebook"])
                        break
    piekey=[k['name'] for k in xtype]
    new_dict={}
    sortkey=[i for i in sorted(list(dict_pub.keys()))]
    for k in sortkey:
        new_dict[k]=dict_pub[k]
    print(new_dict)
    client.close()
    return render_template('index.html',da=xtype,pkey=piekey,
                           mons=list(new_dict.keys()),monDatas=list(new_dict.values()))


if __name__ == '__main__':
    app.run()
