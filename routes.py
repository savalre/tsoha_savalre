from app import app
from flask import render_template, request, redirect, session
import users, db, soitin, gig, admin

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/admin")
def adminsivu():
	paasy = False
	id = session.get("user_id",0)
	if admin.get_role(id):
		paasy = True
		admins = admin.admin_list()
		kayttajat = admin.user_list()
		return render_template("admin.html", admins=admins, kayttajat=kayttajat)
	else:
		return render_template("error.html", message="Sinulla ei ole oikeuksia tälle sivulle, otathan yhteyttä ylläpitoon jos tämä on virhe")

@app.route("/addAdmin",methods=["get"])
def addAdmin():
	print("löysin tänne addAdminiin!")
	id = request.args.get("sid")
	admin.new_admin(id)
	return render_template("adminUpdate.html", message="Adminoikeudet lisätty!") 
	

@app.route("/delAdmin",methods=["get"])
def delAdmin():
	id = request.args.get("sid")
	admin.del_admin(id)
	return render_template("adminUpdate.html",message="Adminoikeudet poistettu!")

@app.route("/login",methods=["get","post"]) 
def login():
		username = request.form["username"]
		password = request.form["password"]
		if users.login(username,password):
			session["username"] = username
			session["user_id"] = users.user_id()
			id = users.user_id()
			
			if admin.get_role(id) == True:
				session["role"] = "admin"
			else:
				session["role"] = "peruskäyttäjä"
				
			session["active_state"] = users.active_state()[0]
			rooli = session.get("role",0)
			print("sessiorooli on: ", rooli)
			return redirect("/")
		else:
			return render_template("error.html",message="Väärä käyttäjätunnus tai salasana :(")
		

@app.route("/logout", methods=["get"])
def logout():
	users.logout()
	return redirect("/")

@app.route("/register",methods=["get","post"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	if request.method == "POST":
		username = request.form["username"]
		password1 = request.form["password1"]
		password2 = request.form["password2"]
		if password1 == password2:
			password = password1;
			if users.register(username,password):
				session["username"] = username
				return redirect("/")
			else:
				return render_template("error.html",message="Hups, rekisteröinti ei onnistunut!")
		else: 
			return render_template("error.html",message="Salasanat eivät ole samat! Kokeile uudestaan")
		
@app.route("/userinfo",methods=["get","post"])
def userinfo():
		soitin = users.get_soitin()
		tila = users.active_state()
		return render_template("userinfo.html", instrument = soitin, state=tila)

@app.route("/edit_user",methods=["get","post"])
def edit_user():
	return render_template("edit_user.html")
	
@app.route("/userUpdated", methods=["post"])
def userUpdated():
	uusitila = request.form["active"]
	soitinvalinta = request.form.getlist("soitin")
	print("sain tiedon:",uusitila, "ja soitinvalinta on: ", soitinvalinta)
	users.muutatila(uusitila)
	users.muutasoitin(soitinvalinta)
	return render_template("update.html", message="Profiilisi on päivitetty!")

@app.route("/keikkasivu")
def keikkasivu():
	lista = gig.gig_list()
	return render_template("keikka.html", keikat=lista)

@app.route("/tulevatKeikat")
def tulevatKeikat():
	lista = gig.gig_list()
	return render_template("tulevatKeikat.html", keikat=lista)

@app.route("/omatKeikat")
def my_gigs():
	id = users.user_id()
	lista = gig.my_gigs(id)
	return render_template("omatKeikat.html",keikat=lista)

@app.route("/newGig")
def uusi_keikka():
	return render_template("addgig.html")

@app.route("/gigAdd",methods=["post"])
def gigAdd():
	nimi = request.form["nimi"]
	pvm = request.form["pvm"]
	time = request.form["aika"]
	paikka = request.form["paikka"]
	kuvaus = request.form["kuvaus"]
	kokoonpano = request.form["kokoonpano"]
	print("Keikkaa lisätään seuraavilla tiedoilla: ", nimi, pvm, time, paikka, kuvaus, kokoonpano)
	if gig.add_gig(nimi,pvm,time,paikka,kuvaus,kokoonpano):
		return render_template("gigUpdate.html",message="Keikka lisätty onnistuneesti!")
	else:
		return render_template("error.html",message="Oho, jotain meni pieleen eikä keikkaa luotu. Yritä uudelleen!")

@app.route("/deleteGig")
def deleteGig():
	id = request.args.get("sid")
	gig.poistaKeikka(id)
	return render_template("gigUpdate.html",message="Keikka poistettu!")

@app.route("/editGig")
def editGig():
	id = request.args.get("sid")
	list = gig.haeTiedot(id)
	print(list)
	return render_template("editGig.html",tiedot=list)

@app.route("/gigEdited", methods=["post"])
def gigEdited():
	id = request.form["keikkaid"]
	nimi = request.form["nimi"]
	pvm = request.form["pvm"]
	time = request.form["aika"]
	paikka = request.form["paikka"]
	kuvaus = request.form["kuvaus"]
	kokoonpano = request.form["kokoonpano"]
	if gig.muokkaaKeikka(id,nimi,pvm,time,paikka,kuvaus,kokoonpano):
		return render_template("gigUpdate.html",message="Keikan tiedot päivitetty!")
	else:
		return render_template("gigUpdate.html",message="Humps, ei onnistunut vaan jotain meni pieleen. :/")
		
@app.route("/ilmo")
def ilmo():
	id = request.args.get("sid")
	userId = users.user_id()
	tiedot= gig.haeTiedot(id)
	soittimet = users.get_soitin()
	return render_template("ilmo.html", tiedot=tiedot, soittimet=soittimet)

@app.route("/ilmoDone", methods=["post"])
def ilmoDone():
	soitin = request.form["soitin"]
	keikkaId = request.form["id"]
	print("tällasella menossa ilmoittautumaan: ", soitin)
	userId = users.user_id()
	gig.lisaaSoittaja(keikkaId,userId,soitin)
	return render_template("gigUpdate.html", message="Ilmoittautuminen onnistui! Tervetuloa keikalle!")

@app.route("/del")
def poistaIlmo():
	keikkaId = request.args.get("sid")
	userId = users.user_id()
	gig.poistaSoittaja(keikkaId,userId)
	return render_template("gigUpdate.html", message= "Poistit ilmoittautumisesi keikalle")

@app.route("/kokoonpano")#tarkastuta tämä
def kokoonpano():
	keikanKokoonpano = request.args.get("skp")
	keikanId = request.args.get("sid")
	keikanTiedot = gig.haeTiedot(keikanId)
	if keikanKokoonpano == "Koko_orkesteri":
		keikanSoittimet = soitin.haeKaikkiSoittimet() # lista keikan soittimista
		print(keikanSoittimet)
		y = len(keikanSoittimet) * 2
		for x in range(0,y,2):
				soitinNimi = keikanSoittimet[x]
				#soitinX = soitinNimi[0]
				soitinId = soitin.haeSoitinid(soitinNimi)
				kp = gig.haeSoittaja(keikanId, soitinId)
				keikanSoittimet.insert(x+1, kp)
				x = x+2
		return render_template("kokoonpano.html", keikanSoittimet = keikanSoittimet, keikanTiedot = keikanTiedot)
	else: 
		keikanSoittimet = soitin.haePienryhmaSoittimet(keikanKokoonpano)
		y = len(keikanSoittimet) * 2
		for x in range(0,y,2):
				soitinNimi = keikanSoittimet[x]
				#soitinX = soitinNimi[0]
				soitinId = soitin.haeSoitinid(soitinNimi)
				kp = gig.haeSoittaja(keikanId, soitinId)
				keikanSoittimet.insert(x+1, kp)
				x = x+2
		return render_template("kokoonpano.html", keikanSoittimet = keikanSoittimet, keikanTiedot = keikanTiedot)
		
