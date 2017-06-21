import colander
import deform.widget
import sys
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_mailer.message import Message

import logging
log = logging.getLogger(__name__)

#Поиск слова в книгах, подсчет и отправка на email
def operate(request,title,email):
    bd = BookData(request)
    res = bd.get_all()
    counts = []
    content_type = 'text/plain'
    
    log.debug('Returning: %s (content-type: %s)', title, content_type)
	
    for row in res:
        count = dict(title=row['title'].encode('utf-8'),author=row['author'].encode('utf-8'),count=row['content'].count(title))
        counts.append(count)
        content = count
        log.debug('Returning: %s (content-type: %s)', content, content_type)

    mail = 'Here is your search results for "'+title+'":\n\n'
    for c in counts:
        if c['count']:
            mail += ' - count:'+str(c['count'])+';\n title:"'+str(c['title'])+'"; author: '+str(c['author'])+'\n\n'
    
    if mail == 'Here is your search results for "'+title+'":\n\n':
        mail = 'There are no search results for "'+title+'"'
	
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(mail)
    msg['Subject'] = 'Search results for "'+title+'"'
    msg['From'] = 'admin@look4book.com'
    msg['To'] = email
    s = smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls()
    s.login('vkiselivskyi@gmail.com', '123asdqwezxc')
    s.sendmail('vkiselivskyi@gmail.com', email, msg.as_string())
    s.quit()
    return mail
    
#Обращения к mongo
class BookData(object):
    def __init__(self, request):
        self.settings = request.registry.settings
        self.collection = request.db.books
		
    def get_all(self):
        books = self.collection.find({})
        return books
		
    def get_all_titles(self):
        books = self.collection.find({},{'title':1})
        return books		
		
#Проверка слова на налачие лишь латинских букв	
def check_letters(node, value, **kwargs):
    val = value.split()
    for v in val:
        v = v.replace("'","")
        if not v.encode("utf-8").isalpha():
	        raise colander.Invalid(node, "Type correct search words (non cyrillic and non numerical)")

			
class Page(colander.MappingSchema):
    title = colander.SchemaNode(colander.String(), validator=check_letters)
    email = colander.SchemaNode(colander.String(), validator=colander.Email())


@view_config(route_name='view', renderer='view.pt')
def view(request):
    schema = Page()
    session = request.session
    form = deform.Form(schema, buttons=('Search',))
    vis = 'none'
    if 'Search' in request.params:
        controls = request.POST.items()
        try:
            values = form.validate(controls)
        except deform.ValidationFailure as e:
            return dict(form = e.render())
			
        session['title'] = values['title']
        session['email'] = values['email'] 
        session['load'] = 0       
        return HTTPFound('/results')
		
    form = form.render()
    return dict(form=form)


@view_config(route_name='view_res', renderer='view_res.pt')
def view_res(request):
    session = request.session
    title = session['title']
    email = session['email']
    if not session['load']:
        res = ''
        session['load'] = 1
        return dict(title=title, email=email, res=res)
    else:
        res = operate(request,title,email)
        return dict(title=title, email=email, res=res)