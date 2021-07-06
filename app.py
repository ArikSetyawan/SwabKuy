from flask import Flask, render_template, redirect, url_for
from peewee import *
import json, requests, time

db = 'swabkuy.db'
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta:
		database=database

class provinsi(BaseModel):
	id = AutoField()
	nama_provinsi = CharField(unique=True)

class kabupatenkota(BaseModel):
	id = AutoField()
	id_provinsi = ForeignKeyField(provinsi)
	nama_kabupatenkota = CharField(unique=True)

class providers(BaseModel):
	id = AutoField()
	id_provinsi = ForeignKeyField(provinsi)
	id_kabupatenkota = ForeignKeyField(kabupatenkota)
	name = CharField()
	test = CharField()
	price = CharField()
	lat = CharField()
	lng = CharField()
	address = TextField()

def create_tables():
	with database:
		database.create_tables([provinsi,kabupatenkota,providers])


app = Flask(__name__)

@app.route('/')
def index():
	return render_template('dashboard.html')

@app.route('/statistics')
def statistics():
	d = []
	data = providers.select(providers.id_kabupatenkota, fn.COUNT(providers.id).alias("jumlah_rs")).group_by(providers.id_kabupatenkota)
	for i in data:
		d.append(i.jumlah_rs)
	
	d.sort(reverse=True)
	high = d[:5]

	# kabupaten dengan rs_terbanyak
	nama_kabupatenkota = [str(i.id_kabupatenkota.nama_kabupatenkota) for i in data if i.jumlah_rs in high]

	count_rs = {'nama_kabupatenkota':nama_kabupatenkota, 'data':high}
	

	""" get covid data: """
	coviddata = requests.get('https://data.covid19.go.id/public/api/update.json')
	coviddata = coviddata.json()

	weekly_data = coviddata['update']['harian'][-30:]
	date = []
	jumlah_positif = []
	jumlah_sembuh = []
	jumlah_meninggal = []
	jumlah_dirawat = []
	for i in weekly_data:
		date.append(time.strftime('%Y-%m-%d',time.localtime(int(i['key']/1000))))
		jumlah_positif.append(i['jumlah_positif']['value'])
		jumlah_sembuh.append(i['jumlah_sembuh']['value'])
		jumlah_meninggal.append(i['jumlah_meninggal']['value'])
		jumlah_dirawat.append(i['jumlah_dirawat']['value'])
		
	weekly_data = {'date':date,'jumlah_positif':jumlah_positif,'jumlah_sembuh':jumlah_sembuh, 'jumlah_meninggal':jumlah_meninggal,'jumlah_dirawat':jumlah_dirawat}

	total_kasus = {
		'keys':list(coviddata['update']['total'].keys()),
		'values': list(coviddata['update']['total'].values())
	}
	return render_template('statistics.html',count_rs=count_rs,weekly_data=weekly_data, total_kasus=total_kasus)

@app.route('/maps')
def maps():
	json_data = providers.select()
	return render_template('mapsv2.html',rows=json_data)

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)