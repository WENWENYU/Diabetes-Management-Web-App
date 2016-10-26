#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
from string import letters
import datetime

import webapp2
import jinja2

from google.appengine.ext import db

import feedparser

template_dir = os.path.join(os.path.dirname(__file__), 'static')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

items = []
#RSS news link: https://news.google.com/news?pz=1&cf=all&q=diabetes&output=rss

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Entry(db.Model):
    date = db.DateProperty(required = True)
    time = db.TimeProperty(required = True)
    glevel = db.IntegerProperty(required = True)
    note = db.TextProperty(required = True)
    username = db.StringProperty(required = True)

class ExerciseLog(db.Model):
    date = db.DateProperty(required = True)
    calories = db.IntegerProperty(required = True)
    duration = db.IntegerProperty(required = True)
    note = db.TextProperty(required = True)
    etype = db.StringProperty(required = True)
    username = db.StringProperty(required = True)

def parse_feed(feed_links):
    #data = parse_feed('')
    '''
        Structure of data returned
        [
            #Item
            [ Identifier_of_source,
              title,
              link,
              description ]
            ...
        ]
    '''
    data = []

    for i in range(len(feed_links)):
        d = feedparser.parse(feed_links[i])
        identifier = d['feed']['title'].lower()
        for post in d.entries:
            item = [identifier.encode('ascii', 'ignore').lower()]
            item.append(post.title.encode('ascii', 'ignore'))
            item.append(post['link'].encode('ascii', 'ignore').lower())
            item.append(post.description)
            data.append(item)
    return data


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class DashboardHandler(BaseHandler):
    def get(self):
        username = self.request.get('username')

        now = datetime.datetime.now()

        try:
            items = db.GqlQuery("SELECT * FROM Entry where username = \'%s\' ORDER BY date DESC, time DESC"%username)
            itemsf = db.GqlQuery("SELECT * FROM Entry where username = \'%s\' and date = DATE(\'"%username + now.strftime('%Y-%m-%d') + "\') ORDER BY time ASC")
            items_rev = db.GqlQuery("SELECT * FROM Entry where username = \'%s\' ORDER BY date ASC, time ASC"%username)
            exercises = db.GqlQuery("SELECT * FROM ExerciseLog where username = \'%s\' and date = DATE(\'"%username + now.strftime('%Y-%m-%d') + "\')")

            ditemsf = []
            dates = []
            duration = 0
            total_calories = 0

            if exercises:
                for exercise in exercises:
                    duration = duration + exercise.duration
                    total_calories = total_calories + exercise.calories

            for item in items_rev:
                entity = Entry(date = item.date, time = item.time, glevel = item.glevel, note = item.note, username = item.username)
                n = 0
                index = 0
                for item2 in ditemsf:
                    if(item2.date == item.date):
                        n = 1
                    else:
                        index = index + 1
                if n == 1:
                    averagecal = (ditemsf[index].glevel + entity.glevel) / 2
                    ditemsf[index].glevel = averagecal
                else:
                    dates.append(item.date.strftime("%Y-%m-%d"))
                    ditemsf.append(entity)

            last_reading = items[0].glevel
            last_reading_date = items[0].date.strftime("%Y-%m-%d") + " @ " + items[0].time.strftime("%H:%M")
            sum = 0
            for i in range(items.count()):
                sum = sum + items[i].glevel
            avg = sum / items.count()
            hba1c = round((77.3 + avg) / 35.6, 2) #change this using formula later
            self.render('dashboard.html', duration = duration, calories_today = total_calories, n = itemsf.count(), initdate = dates[0], findate = dates[len(ditemsf) - 1], dates = dates, dcount = len(ditemsf), ditemsf = ditemsf, itemsf = itemsf, username = username, count = items.count(), items = items, last_reading = last_reading, last_reading_date = last_reading_date, avg = avg, hba1c = hba1c)
        except:
            self.render('dashboard.html', duration = 0, calories_today = 0, n = 0, dcount = 0, count = 0, username = username)
            print ""

class ReadingsHandler(BaseHandler):
    def post(self):
        note = self.request.get('note')
        glevel = self.request.get('glevel')
        time = self.request.get('time')
        date = self.request.get('date')
        username = self.request.get('username')

        if note and glevel and time and date:
            entity = Entry(note = note, glevel = int(glevel), time = datetime.datetime.strptime(time, "%I:%M%p").time(), date = datetime.datetime.strptime(date, "%Y-%m-%d").date(), username = username)
            entity.put()

            items = db.GqlQuery("SELECT * FROM Entry where username = \'%s\' ORDER BY date DESC, time DESC"%username)
            self.redirect("/readings?username=" + username)
            self.render('readings.html', items = items, username = username, note = note, glevel = glevel, time = time, date = date)

    def get(self):
        username = self.request.get('username')
        try:
            items = db.GqlQuery("SELECT * FROM Entry where username = \'%s\' ORDER BY date DESC, time DESC"%username)
            self.render('readings.html', items = items, username = username)
        except:
            self.render('readings.html', items = items, username = username)

class ExerciseHandler(BaseHandler):
    def post(self):
        calories = self.request.get('calories')
        etype = self.request.get('type')
        duration = self.request.get('duration')
        date = self.request.get('date')
        note = self.request.get('note')
        username = self.request.get('username')

        if note and calories and duration and etype and date:
            entity = ExerciseLog(note = note, calories = int(calories), duration = int(duration), date = datetime.datetime.strptime(date, "%Y-%m-%d").date(), etype = etype, username = username)
            entity.put()
            items = db.GqlQuery("SELECT * FROM ExerciseLog where username = \'%s\' ORDER BY date DESC"%username)
            self.redirect("/exercise?username=" + username)
            self.render('exercise.html', items = items, username = username, note = note, calories = calories, duration = duration, type = etype, date = date)

    def get(self):
        username = self.request.get('username')
        try:
            items = db.GqlQuery("SELECT * FROM ExerciseLog where username = \'%s\' ORDER BY date DESC"%username)
        except:
            print ''
        self.render('exercise.html', items = items, username = username)

class NewsHandler(BaseHandler):
    def get(self):
        username = self.request.get('username')
        feed_data = parse_feed(["https://news.google.com/news?pz=1&cf=all&q=diabetes&output=rss"])

        self.render('news.html', feed = feed_data, username = username)

class ContactHandler(BaseHandler):
    def get(self):
        username = self.request.get('username')
        self.render('contact.html', username = username)

class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/dashboard', DashboardHandler),
    ('/readings', ReadingsHandler),
    ('/exercise', ExerciseHandler),
    ('/news', NewsHandler),
    ('/contact', ContactHandler)
], debug=True)
