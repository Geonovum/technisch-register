

from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from bs4 import BeautifulSoup as BS
from json import load
from os import chmod
from stat import S_IRWXO, S_IRWXG, S_IRWXU
from subprocess import call
import codecs

def create_standard_title(title, description):
	title = '''
		<h2>%s</h2>
		<p>%s</p>
		''' % (title, description)

	# use python's built-in parser which skips
	# creation of html and body tags
	return BS(title, 'html.parser')

def create_substandard_title(standard, artifact, title):
	title = '''
		<p><i class="fa fa-file-o"></i>
			<span style='margin-left: 25px'>
				<a href="http://register.geostandaarden.nl/%s/%s">%s</a>
			</span>
		</p> ''' % (artifact, standard, title)

	return BS(title, 'html.parser')

def create_substandard_description(substandard):
	summary ='''
		<p>
			<span style='margin-left:37px; width: 100%%'>%s</span>
		</p>
		''' % substandard['beschrijving']

	return BS(summary, 'html.parser')

def create_standard_webpage(standard, artifacts):
	# builds each standard's overview page
	# e.g. http://register.geostandaarden.nl/imgeo/

	# load standard HTML template
	with open('../web/templates/standard.html', 'r') as f:
		html = BS(f)

	# construct title
	title = create_standard_title(standard['title'], standard['beschrijving'])
	
	# add to #title div
	el_title = html.find(id="title")

	# fetch #container from template
	el_container = html.find(id="container")

	# append title
	el_title.append(title)

	with codecs.open('../descriptions.json', encoding='utf8') as f:
		descriptions = load(f)

	# iterate over all artifacts i.e. informatiemodel, gmlapplicatieschema, regels, etc.
	for artifact in artifacts:
		# create title of each sub standard
		title = create_substandard_title(standard['id'], artifact, descriptions[artifact]['titel'])
		el_container.append(title)

		# create description of each standard
		description = create_substandard_description(descriptions[artifact])
		el_container.append(description)

	return html.prettify()

def create_overview_entry(standard, description):
	# url = "http://register.geostandaarden.nl"
	url = "."
	overview = '''
		<p>
			<i class="fa fa-file"></i>
			<span style='margin-left: 25px'>
				<a href="%s/%s/index.html">%s</a>
			</span>
		</p>
		<p><span style='margin-left:37px; width: 100%%'>%s</span></p>
			''' % (url, standard, standard.upper(), description)

 	return BS(overview, 'html.parser')

def create_overview_page(standards, source, destination):
	print 'Creating overview page...'

	# open overview page template
	with codecs.open('../web/templates/overview.html', 'r', encoding='utf8') as f:
		html = BS(f)

	el_container = html.find(id='leftcolumn')

	for standard in standards:
		overview = create_overview_entry(standard['id'], standard['beschrijving'])
		el_container.append(overview)

	with codecs.open('%s/index.html' % destination, 'w', encoding='utf8') as f:
		f.write(html.prettify())
		#OSFS('./').copydir('../web/assets', '%s/assets' % destination)
		call('cp -r ../web/assets %s/assets' % destination)

		print 'Done!'

def build_folders(source, destination, standards, root):
	print "Building register..."

	source_fs = OSFS(source)

	# iterate over all standards in source directory
	for standard in standards:
		print "Processing %s ... " % standard['id']
		standard_fs = source_fs.opendir(standard['id'])

		# list all sub standards of a standard
		artifacts = standard_fs.listdir(dirs_only=True)
		if '.git' in artifacts: artifacts.remove(".git")

		for artifact in artifacts:
			# check whether artifact folder exists in destination 
			if root.exists('%s/%s' % (destination, artifact)) == False:
				root.makedir('%s/%s' % (destination, artifact))
				
			# copy standard folders from source to destination in desired structure
			root.copydir('%s/%s/%s' % (source, standard['id'], artifact),  '%s/%s/%s' % (destination, artifact, standard['id']))

		# create standard HTML page
		html = create_standard_webpage(standard, artifacts)

		# check whether standard folder exists in register root
		if root.exists('%s/%s' % (destination, standard['id'])) == False:
			root.makedir('%s/%s' % (destination, standard['id']))
		
		# write standard HTML page to register/standard/index.html
		with codecs.open('%s/%s/index.html' % (destination, standard['id']), 'w', encoding='utf8') as f:
			f.write(html)

def fetch_repos(root, destination, repos):
	print "Fetching repositories..."

	for repo in repos:
		print "Cloning %s in repos/%s" % (repo['url'], repo['id'])
		# explicitely create dir as implicit cration fails on server
		root.makedir('%s/%s' % (destination, repo['id']))
		call('git clone %s repos/%s' % (repo['url'], repo['id']), shell=True)

	#TODO: git pull additions into existing repos, clone new ones


if __name__ == "__main__":
	source = 'repos'
	destination = 'register2'

	root = OSFS('./') # 'c:\Users\<login name>' on Windows
	
	
	try:
		print "removing %s" % source
		# removedir function cannot deal with protected
		# files in each repo's .git folder
		call('rm -rf %s' % source, shell=True)
	except ResourceNotFoundError: 
		print "Failed to remove %s..." % source

	try:
		print "removing %s" % destination
		root.removedir(destination, force=True)
	except ResourceNotFoundError:
		print "Failed to remove %s..." % destination
	
	root.makedir(source)
	# chmod(source, S_IRWXU | S_IRWXG | S_IRWXO)
	root.makedir(destination)
	# chmod(destination, S_IRWXU | S_IRWXG | S_IRWXO)

	#standards = OSFS(source).listdir(dirs_only=True)
	with open('../repos.json') as f:
		standards = load(f)
	
	fetch_repos(root, destination, standards)
	build_folders(source, destination, standards, root)
	create_overview_page(standards, source, destination)

	print 'Copying register to staging...'
	# remove staging
	# create staging
	# makie staging writable
	# OSFS('register').removedir('staging', force=True)
	call('rm -rf ../register/staging', shell=True)


	call('mv %s ../register/staging' % destination, shell=True)
	# root.copydir(destination, '../register/staging')
	# root.removedir(destination, force=True)
	
	call('rm -rf %s' % source, shell=True)
	# root.removedir(source, force=True)

