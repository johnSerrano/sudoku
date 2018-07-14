import json
import webapp2
import sudoku


class ApiHandler(webapp2.RequestHandler):
    def post(self):
        r = json.loads(self.request.body)
        board = sudoku.SudokuBoard(r['board'])
        try:
            ok, msg = sudoku.find_solution(board, 60)
        except sudoku.TimeoutException:
            response = {'ok': False, 'msg': 'Timed out after 1 minute'}
        else:
            response = {'ok': ok, 'msg': msg}

        self.response.headers['content-type'] = 'application/json'
        self.response.write(json.dumps(response))

    def get(self):
        self.response.headers['content-type'] = 'text/plain'
        self.response.write('OK')


app = webapp2.WSGIApplication([
    ('/api/.*', ApiHandler)
])

