from flask import Flask, render_template,request, session, redirect, url_for, escape
import psycopg2
app = Flask(__name__,static_url_path='/static')
app.secret_key='random'

conn=psycopg2.connect("dbname=elec_select user=postgres")
cur=conn.cursor()
#all_tb=cur.execute('\dt')
usn=0
nm=0
sem=0
dep=0
sub=[]
res1=[]
ses_list=[]
elec_list=[]
mega_list=[]

@app.route('/info')
def sel():
	return render_template('information.html',usn=usn,name=nm,sem=sem,dep=dep)
	
@app.route('/update',methods = ['POST', 'GET'])
def update():
	if(request.method=="POST"):
		try:
			l_usn="\'"+usn.strip()+"\'"
			up=request.form['ses_pick']
			up="\'"+up+"\'"
			print(up)
			cur.execute("insert into takes values ({usn},{up},'{status}')".format(usn=l_usn,up=up,status='In_Progress'))
			cur.execute("update takenby set current_strength=current_strength+1 where session_id={si}".format(si=up))
			#print('done')
			cur.execute("select * from takes")
			print(cur.fetchall())
			
		except:
			conn.rollback()
		finally:
			return render_template('elec.html',usn=usn,name=nm,sem=sem,dep=dep,electives=elec_list,sessions=ses_list)
		
			
	
@app.route('/info',methods = ['POST', 'GET']) #more information page
def speci():
	global res1
	if(request.method=="POST"):
		try:
			sp=request.form["pick"]
			ip=request.form["input"]
			print(sp)
			print(ip)
			if(sp=='specil'):
				cur.execute("Select e.name from elective as e,specialisation as s where s.name='{special}' and s.electiveid=e.electiveid".format(special=ip))
				#res1=cur.fetchall()
				#print(a)
				modal=1
			elif(sp=='sesid'):
				cur.execute("Select fname, lname from student as s, takes as t where s.USN=t.USN and t.session_id='{sess}'".format(sess=ip))
				modal=2
				#res1=[x[0]+" "+x[1] for x in res1]
			elif(sp=='elecid'):
				cur.execute("select name from specialisation where electiveid='{elec}'".format(elec=ip))
				modal=3
				#print(a)
				#res1=cur.fetchall()
				#print(res1)
				
			res1=cur.fetchall()
			print(res1)
			print("result=",res1)
		except:
			conn.rollback()
		finally:
			return render_template('information.html', result=res1, modal=modal,usn=usn,name=nm,sem=sem,dep=dep)
			

@app.route('/select')     #pick which table to display, basic 
def select():
	return render_template('select.html')
	
@app.route('/login')   #render the login form 
def login():
	if request.method == 'POST':
		session['username'] = request.form['uname']
		usn=request.form['uname']
		print(usn)
		return redirect(url_for('index'))
	return render_template('login.html')
	
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('uname', None)
   return redirect(url_for('login'))
   
@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
	return "<h1>You are not logged in </h1><br><a href = '/login'></b>" + "click here to log in</b></a>"
	
@app.route('/details') #show details every other time
def updated():
	#print(usn)
	Usn="\'"+str(usn).strip()+"\'"
	#print(Usn)
	cur.execute("Select e.name,t.status from elective as e, takenby as tb, student as s,takes as t where s.USN={usn} and s.USN=t.USN and t.session_id=tb.session_id and tb.elective_id=e.electiveid".format(usn=Usn))
	sub=cur.fetchall()
	#sub=[x[0] for x in sub]
	print(sub)
	sub=[list(x) for x in sub]
	#print(sub)
	for x in sub:
		x.append('Elective')
	print("ere",sub)
	#sub=[x[0] for x in sub]
	cur.execute("Select c.name,ccs.status from corecourses as c,ccstatus as ccs where ccs.USN={usn} and ccs.courseid=c.courseid".format(usn=Usn))
	core=cur.fetchall()
	core=[list(x) for x in core]
	for x in core:
		x.append('Core')
	sub+=core
	return render_template('details.html',usn=usn,name=nm,sem=sem,dep=dep,cur_courses=sub)
	
@app.route('/details',methods=['POST','GET'])  #show the personal details page on login (only the first time)
def details():
	global usn,nm,sem,dep,sub
	print(usn)
	
	#a=cur.fetchall()
	#print(a)
	
	print(sub)
	if(request.method=='POST'):
		try:
			un=request.form['uname']
			pw=request.form['psw']
			cur.execute("select * from student")
			all_stud=cur.fetchall()
			all_stud=[x[0].strip(' ') for x in all_stud]
			#print(all_stud)
			#print(un)
			#print(pw)
			#print(un==pw and un in all_stud)
			if(un==pw and un in all_stud):
				#	print("here")
				#cur.execute("select USN,fname,lname,current_sem,department from student where USN={usn}".format(usn=un))
				Usn="\'"+un+"\'"
				#sql="Select * from student where USN='01FB14E002';"
				#data=str(un)
				#print("data",data)
				cur.execute("Select * from student where USN={usn}".format(usn=Usn))
				#print(a)
				#print("here now")
				student=cur.fetchone()
				#print(student)
				#print(a)
				usn=student[0]
				nm=student[4]+" "+student[5]
				sem=student[8]
				dep=student[7]
				#print(usn)
				#print(nm)
				#print(sem)
				#print(dep)
				#print("done")
				#usn="\'"+usn+"\'"
				Usn="\'"+str(usn).strip()+"\'"
				#print(Usn)
				cur.execute("Select e.name,t.status from elective as e, takenby as tb, student as s,takes as t where s.USN={usn} and s.USN=t.USN and t.session_id=tb.session_id and tb.elective_id=e.electiveid".format(usn=Usn))
				sub=cur.fetchall()
				#print(sub)
				sub=[list(x) for x in sub]
				#print(sub)
				for x in sub:
					x.append('Elective')
				#print("ere",sub)
				#sub=[x[0] for x in sub]
				cur.execute("Select c.name,ccs.status from corecourses as c,ccstatus as ccs where ccs.USN={usn} and ccs.courseid=c.courseid".format(usn=Usn))
				core=cur.fetchall()
				core=[list(x) for x in core]
				for x in core:
					x.append('Core')
				sub+=core
				print(sub)
				#return render_template('details.html',usn=usn,name=nm,sem=sem,dep=dep)						
			
		except:
			conn.rollback()
		finally:
			#return render_template('details.html',usn=un)
			return render_template('details.html',usn=usn,name=nm,sem=sem,dep=dep,cur_courses=sub)
			#return render_template('hello.html')
	else:
		return render_template('details.html',usn=usn,name=nm,sem=sem,dep=dep,cur_courses=sub)
		
'''	
@app.route('/elec') #list all electivs the student can currently take
def elec():
	global ses_list,elec_list,mega_list
	#cur.execute("select electiveid, name, rating from elective where did='CS' and sem>{cur_sem} and electiveid not in(select tb.elective_id from takes as t, takenby as tb where USN='{usn}' and tb.session_id=t.session_id)".format(cur_sem=sem,usn=usn))
	cur.execute("select name from elective")
	all_elec=cur.fetchall()
	#print(usn)
	for i in all_elec:
		a=cur.mogrify(("select distinct e.electiveid,e.name,e.rating "
"from sessions as s,takenby as tb,student as st, elective as e,professors as p "
"WHERE s.session_id=tb.session_id and tb.elective_id=e.electiveid and e.name='{e}' "
"and tb.cutoff<(select cgpa from student where USN='{usn}') and p.p_id=tb.p_id " 
"and exists( select name from elective natural join prereq natural join ccstatus " 
"WHERE USN='{usn}' and name='{e}' and status='Pass')").format(usn=str(usn).strip(),e=i[0]))
		print(a)
		#print("hello")
		#print(i[0])
		#cur.execute("select distinct e.electiveid,e.name,e.rating from sessions as s,takenby as tb,student as st, elective as e,professors as p WHERE s.session_id=tb.session_id and tb.elective_id=e.electiveid and e.name='{e}' and tb.cutoff<(select cgpa from student where USN='{usn}') and p.p_id=tb.p_id and exists( select name from elective natural join prereq natural join ccstatus WHERE USN='{usn}' and name='{e}' and status='Pass')".format(usn=str(usn).strip(),e=i[0]))
		cur.execute(("select distinct e.electiveid,e.name,e.rating "
"from sessions as s,takenby as tb,student as st, elective as e,professors as p "
"WHERE s.session_id=tb.session_id and tb.elective_id=e.electiveid and e.name='{e}' "
"and tb.cutoff<(select cgpa from student where USN='{usn}') and p.p_id=tb.p_id " 
"and exists( select name from elective natural join prereq natural join ccstatus " 
"WHERE USN='{usn}' and name='{e}' and status='Pass')").format(usn=str(usn).strip(),e=i[0]))
		#print(a)
		temp=cur.fetchall()
		#print(i[0],temp)
		mega_list.append(temp)
		
	mega_list=[x for x in mega_list if x!=[]]
	print(mega_list)
	#elec_list=set([[x[0],x[1],x[2]] for x in mega_list])
	#print(elec_list)
	iter_list=["\'"+x[0][1]+"\'" for x in mega_list]
	print(iter_list)
	ses_list=[]
	for i in iter_list:
		print(i)
		#cur.execute("select session_id, p.name from professors as p, takenby as tb where tb.p_id=p.p_id and tb.elective_id={e} and tb.current_strength<tb.no_of_students".format(e=i))
		#res=cur.fetchall()
		#print(res)
	#for i in range(mega_list):
		cur.execute("select distinct s.session_id,p.name from sessions as s,takenby as tb,student as st, elective as e,professors as p WHERE s.session_id=tb.session_id and tb.elective_id=e.electiveid and e.name='{e}' and tb.cutoff<(select cgpa from student where USN='{usn}') and p.p_id=tb.p_id and exists( select name from elective natural join prereq natural join ccstatus WHERE USN='{usn}' and name='{e}' and status='Pass')".format(usn=str(usn).strip(),e=i))
		ses_list.append(cur.fetchall())
		print(ses_list)			
	return render_template('elec.html',usn=usn,name=nm,sem=sem,dep=dep,electives=elec_list,sessions=ses_list)'''
	

@app.route('/elec')
def elec():
	global ses_list,elec_list
	cur.execute("select electiveid, name, rating from elective where did='CS' and sem>{cur_sem}".format(cur_sem=sem))
	elec_list=cur.fetchall()
	#print(elec_list)
	iter_list=["\'"+x[0]+"\'" for x in elec_list]
	ses_list=[]
	for i in iter_list:
		cur.execute("select session_id, p.name from professors as p, takenby as tb where tb.p_id=p.p_id and tb.elective_id={e} and tb.current_strength<tb.no_of_students".format(e=i))
		res=cur.fetchall()
		#print(res)
		ses_list.append(res)
		#print(ses_list)			
	return render_template('elec.html',usn=usn,name=nm,sem=sem,dep=dep,electives=elec_list,sessions=ses_list)
	
	
@app.route('/display',methods = ['POST', 'GET'])  #to display the table picked in select, generic 
def display():
	if(request.method=="POST"):
		try:
			tb=request.form["table"]
			print(tb)
			#tb2=request.form["student"]
			cur.execute("select * from {table} where false".format(table=tb))
			tb_head=cur.fetchall()
			print(tb_head)
			cur.execute("select * from {table}".format(table=tb))
			res=cur.fetchall()
			#print(res)
		except:
			conn.rollback()
		finally:
			return render_template('result.html', result = res,heading=tb,tb_head=tb_head)
			
@app.route('/special')
def spel():
	cur.execute("select distinct s.name from specialisation as s")
	n=cur.fetchall()
#	print(n)
	res=[]
	for i in n:
		cur.execute("select count(*) from ((Select distinct tb.elective_id from student as s,takes as t, specialisation as sp,elective as e, takenby as tb where s.USN=t.usn and s.USN='01FB15ECS005' and t.session_id=tb.session_id) INTERSECT (Select sp.electiveid from specialisation as sp where sp.name='{sname}')) as T".format(sname=i[0]))
		count=cur.fetchall()
		if int(count[0][0])>=4:

			res.append(i)
	print(res)
	return render_template('spec.html', result=res,usn=usn,name=nm,sem=sem,dep=dep)

if __name__ == '__main__':
   app.run(debug = True)
