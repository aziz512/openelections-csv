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
import webapp2
import csv
import json
import StringIO
from google.appengine.ext import ndb


class PrecinctVotes(ndb.Model):
    precinct = ndb.StringProperty()
    county = ndb.StringProperty()
    votes = ndb.JsonProperty()

def process_csv(csv_data):
    precinct_to_votes = {} #final data object
    precincts = [] #list of unique precints
    precinctCounties = {}
    f = StringIO.StringIO(csv_data)
    rows = list(csv.reader(f, delimiter=',' ))
    #remove header
    del rows[0]
    #getting the list of unique precincts
    for i in range(len(rows)):
        if not rows[i][1] in precincts:
            precincts.append(rows[i][1])
            precinctCounties[rows[i][1]] = rows[i][0]
    for precinct in precincts:
        precinct_candidates = list(filter(lambda x: x[1] == precinct and x[2] == 'President',rows))
        candidates = {}
        #avoid duplicate names
        for candidate in precinct_candidates:
            if not candidate[5] in candidates:
                candidates[candidate[5]] = candidate[6]
            else:
                #if duplicate just add up votes
                candidates[candidate[5]] = int(candidates[candidate[5]]) + int(candidate[6])
        #saving candidates dict into the main data output
        precinct_to_votes[precinct] = PrecinctVotes(id = precinctCounties[precinct] + '__' + precinct , county = precinctCounties[precinct], precinct = precinct, votes = candidates)

    return precinct_to_votes


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')
class UploadHandler(webapp2.RequestHandler):
    def post(self):
        csv_data = self.request.POST.get('csv-file').file.read()
        results = process_csv(csv_data)
        for key in results:
            results[key].put()
        self.response.write('done')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler)
], debug=True)
