from bs4 import BeautifulSoup as BS
from settings import build_path
from json import load
from subprocess import call
from os import path as ospath
import codecs


def create_standard_title(title, description):
    title = '''
        <h2>%s</h2>
        <p>%s</p>
        ''' % (title, description)

    # use python's built-in parser since
    # it does not create html and body tags
    return BS(title, 'html.parser')

def create_artifact_title(standard, artifact, title):
    title = '''
        <p><i class="fa fa-file-o"></i>
            <span style='margin-left: 25px'>
                <a href="https://register.geostandaarden.nl/%s/%s">%s</a>
            </span>
        </p> ''' % (artifact, standard, title)

    return BS(title, 'html.parser')

def create_artifact_description(artifact):
    summary ='''
        <p>
            <span style='margin-left:37px; width: 100%%'>%s</span>
        </p>
        ''' % artifact['beschrijving']

    return BS(summary, 'html.parser')

def create_standard_webpage(standard, artifacts, assets_path):
    """Build a standard's overview page
    
    e.g. https://register.geostandaarden.nl/imgeo/
    """

    # load standard HTML template
    with open(ospath.join(assets_path, 'web', 'templates', 'standard.html'), 'r') as f:
        html = BS(f, 'html.parser')
    
    # fetch title element from template
    el_title = html.find(id="title")

    # fetch #container element from template
    el_container = html.find(id="container")

    # construct title
    title = create_standard_title(standard['titel'], standard['beschrijving'])

    # append title to #title div
    el_title.append(title)

    with codecs.open(ospath.join(assets_path, 'descriptions.json'), encoding='utf8') as f:
        descriptions = load(f)

    # iterate over all artifacts i.e. informatiemodel, gmlapplicatieschema, regels, etc.
    for artifact in artifacts:
        # create title of each artifact
        title = create_artifact_title(standard['id'], artifact, descriptions[artifact]['titel'])
        el_container.append(title)

        # create description of each standard
        description = create_artifact_description(descriptions[artifact])
        el_container.append(description)

    informatiemodel_link = html.find(id="breadctxt").findAll('a')[-1]
    standard_title = standard['titel_kort']
    informatiemodel_link['href'] = "https://register.geostandaarden.nl/" + standard_title.lower()
    informatiemodel_link.string = standard_title

    return html.prettify()

def create_overview_entry(standard, title_short, description):
    # url = "https://register.geostandaarden.nl"
    url = "."
    overview = '''
        <p>
            <i class="fa fa-file"></i>
            <span style='margin-left: 25px'>
                <a href="%s/%s/index.html">%s</a>
            </span>
        </p>
        <p><span style='margin-left:37px; width: 100%%'>%s</span></p>
            ''' % (url, standard, title_short, description)

    # print standard
    return BS(overview, 'html.parser')

def create_cluster_overview(standards, source, destination_temp, repoCluster, root, assets_path):
    """Creates a cluster's overview page

    e.g.https://register.geostandaarden.nl/brt/index.html
    """

    print 'Creating cluster overview page...'
    
    # open overview page template
    with codecs.open(ospath.join(assets_path, 'web', 'templates', 'overview.html'), 'r', encoding='utf8') as f:
        html = BS(f, 'html.parser')
        
    el_container = html.find(id='leftcolumn')

    for standard in standards:
        if standard['cluster'] == repoCluster:
            overview = create_overview_entry(standard['id'], standard['titel_kort'], standard['beschrijving_kort'])
            el_container.append(overview)

    with codecs.open(ospath.join(build_path, destination_temp, repoCluster, 'index.html'), 'w', encoding='utf8') as f:
            f.write(html.prettify())
        #OSFS('./').copydir('../web/assets', '%s/assets' % destination_temp)
        # call('cp -r web/assets %s/assets' % destination_temp, shell=True)

    print 'Done!'
        
def create_register_homepage(clusters, source, destination_temp):
    """Creates the register's homepage

    https://register.geostandaarden.nl
    """

    print 'Creating overview page...'
    
    # open overview page template
    with codecs.open('web/templates/overview.html', 'r', encoding='utf8') as f:
        html = BS(f, 'html.parser')

    el_container = html.find(id='leftcolumn')

    for cluster in clusters:
        # print cluster['id']
        overview = create_overview_entry(cluster['id'], cluster['titel_kort'], cluster['beschrijving_kort'])
        el_container.append(overview)

    with codecs.open(ospath.join(build_path, destination_temp, 'index.html'), 'w', encoding='utf8') as f:
        f.write(html.prettify())
        #OSFS('./').copydir('../web/assets', '%s/assets' % destination_temp)
        # call('cp -r web/assets %s/assets' % destination_temp, shell=True)

        print 'Done!'