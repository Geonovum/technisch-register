from fs.osfs import OSFS
from bs4 import BeautifulSoup as BS
from json import load
import codecs


def create_title(title, description):
	title = '''
		<h2>%s</h2>
		<p>%s</p>
	''' % (title, description)

	# use python's built-in parser which skips
	# creation of html and body tags
	return BS(title, 'html.parser')

def create_substandard_title(standard, sub_standard):
	title = '''
	<p>
		<i class="fa fa-file-o"></i>
		<span style='margin-left: 25px'>
			<a href="http://register.geostandaarden.nl/%s/%s">%s</a>
		</span>
	</p>
	''' % (sub_standard, standard, sub_standard.capitalize())

	return BS(title, 'html.parser')

def create_substandard_description(description):
	summary = '''
	<p>
		<span style='margin-left:37px; width: 100%%'>%s</span>
	</p>
	''' % description

	return BS(summary, 'html.parser')


def build_web_page(standard, sub_standards, descriptions_path):
	# builds each standard's overview page
	# e.g. http://register.geostandaarden.nl/imgeo/

	print descriptions_path

	try:
		# open standard configuration file that contains descriptions for each sub standard
		with open(descriptions_path, 'r') as f:
			descriptions = load(f)

	except IOError:
		print "Warning, couldn't find configuration file for %s" % standard

		# return empty HTML page
		return ""

	# load standard HTML template
	with open('web/templates/standard.html', 'r') as f:
		html = BS(f)

	# construct title
	title = create_title(descriptions['title'], descriptions['description'])
	
	# add to #title div
	el_title = html.find(id="title")
	# fetch #container from template
	el_container = html.find(id="container")

	# append title
	el_title.append(title)

	# iterate over all sub_standards i.e. informatiemodel, gmlapplicatieschema, regels, etc.
	for sub_standard in sub_standards:
		# create title
		title = create_substandard_title(standard, sub_standard)
		el_container.append(title)

		try:
			description = create_substandard_description(descriptions['sub_standards'][sub_standard])
		except KeyError:
			description = ""

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
	# open overview page template
	with codecs.open('web/templates/overview.html', 'r', encoding='utf8') as f:
		html = BS(f)

	el_container = html.find(id='leftcolumn')

	# iterate over standaards
	for standard in standards:
		print standard
		try:
			with open('%s/%s/configuratie.json' % (source, standard)) as f:
				description = load(f)
		except IOError:
			print "Warning, could not find configuration file for %s " % standard
			continue

		# if 'informatiemodel' in description:
		overview = create_overview_entry(standard, description['description'])
		el_container.append(overview)

	with codecs.open('%s/index.html' % destination, 'w', encoding='utf8') as f:
		print html
		f.write(html.prettify())

		# OSFS('./').copydir('web/assets', '%sassets' % destination)

	# copy web assets to ./register/assets


def build_folders(source, destination, standards, root):
	source_fs = OSFS(source)

	# iterate over all standards in sources directory
	for standard in standards:
		print standard
		standard_fs = source_fs.opendir(standard)

		# list all sub standards of a standard
		sub_standards = standard_fs.listdir(dirs_only=True)
		if '.git' in sub_standards: sub_standards.remove(".git")

		# iterate over all sub standards
		for sub_standard in sub_standards:
			# check whether sub_standard folder exists in root
			if root.exists('%s/%s' % (destination, sub_standard)) == False:
				root.makedir('%s/%s' % (destination, sub_standard))
				
			root.copydir('%s/%s/%s' % (source, standard, sub_standard),  '%s/%s/%s' % (destination, sub_standard, standard))

		html = build_web_page(standard, sub_standards, source + '/' + standard + '/configuratie.json')

		if root.exists('%s/%s' % (destination, standard)) == False:
			root.makedir('%s/%s' % (destination, standard))
		
		with open('%s/%s/index.html' % (destination, standard), 'w') as f:
			f.write(html)

if __name__ == "__main__":
	source = 'repos'
	destination = 'register'

	root = OSFS('./') # 'c:\Users\<login name>' on Windows
	root.removedir(destination, force=True)
	root.makedir(destination)

	standards = OSFS(source).listdir(dirs_only=True)
	build_folders(source, destination, standards, root)

	create_overview_page(standards, source, destination)