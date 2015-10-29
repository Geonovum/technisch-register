from bs4 import BeautifulSoup as BS
from json import load
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

def create_artifact_title(standard, artifact, title):
    title = '''
        <p><i class="fa fa-file-o"></i>
            <span style='margin-left: 25px'>
                <a href="http://register.geostandaarden.nl/%s/%s">%s</a>
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

def create_standard_webpage(standard, artifacts):
    """Build a standard's overview page
    e.g. http://register.geostandaarden.nl/imgeo/
    """

    # load standard HTML template
    with open('web/templates/standard.html', 'r') as f:
        html = BS(f)

    # construct title
    title = create_standard_title(standard['titel'], standard['beschrijving'])
    
    el_title = html.find(id="title")

    # fetch #container from template
    el_container = html.find(id="container")

    # append title to #title div
    el_title.append(title)

    with codecs.open('descriptions.json', encoding='utf8') as f:
        descriptions = load(f)

    # iterate over all artifacts i.e. informatiemodel, gmlapplicatieschema, regels, etc.
    for artifact in artifacts:
        # create title of each artifact
        title = create_artifact_title(standard['id'], artifact, descriptions[artifact]['titel'])
        el_container.append(title)

        # create description of each standard
        description = create_artifact_description(descriptions[artifact])
        el_container.append(description)

    return html.prettify()

def create_overview_entry(standard, title_short, description):
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
            ''' % (url, standard, title_short, description)

    return BS(overview, 'html.parser')

def create_overview_page(standards, source, destination_temp):
    print 'Creating overview page...'

    # open overview page template
    with codecs.open('web/templates/overview.html', 'r', encoding='utf8') as f:
        html = BS(f)

    el_container = html.find(id='leftcolumn')

    for standard in standards:
        overview = create_overview_entry(standard['id'], standard['titel_kort'], standard['beschrijving_kort'])
        el_container.append(overview)

    with codecs.open('%s/index.html' % destination_temp, 'w', encoding='utf8') as f:
        f.write(html.prettify())
        #OSFS('./').copydir('../web/assets', '%s/assets' % destination_temp)
        # call('cp -r web/assets %s/assets' % destination_temp, shell=True)

        print 'Done!'