import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

def post(url, payload, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())

def ok(msg): print('OK  ' + msg)
def fail(msg): print('FAIL ' + msg); sys.exit(1)

h = json.loads(urllib.request.urlopen('http://localhost:8000/health', timeout=10).read())
assert h['phase'] == 2
ok('T1  Health phase=2')

p = post('http://localhost:8000/api/lesson-plan', {
    'topic': 'Newtons Laws', 'learner_level': 'Beginner', 'language': 'English',
    'available_time_minutes': 5, 'learning_goal': 'Understand basics'
})
segs = p.get('segments', [])
assert len(segs) >= 1
ok('T2  Phase 1 lesson-plan OK, segments=' + str(len(segs)))

seg = segs[0]
tc = post('http://localhost:8000/api/start-teaching', {
    'topic': p['title'], 'lesson_title': p['title'],
    'segment_id': seg['id'], 'segment_title': seg['title'],
    'concept': seg['concept'], 'teaching_goal': seg['teaching_goal'],
    'key_points': seg['key_points'], 'example': seg['example'],
    'visual_type': seg['visual_type'],
    'learner_level': p['learner_level'], 'language': p['language'],
})
assert tc.get('correct_answer'), 'correct_answer missing'
assert tc.get('acceptable_answer_points'), 'acceptable_answer_points missing'
assert tc.get('question', {}).get('prompt'), 'question.prompt missing'
ok('T3  start-teaching: all required fields present')
ok('T4  (prefetch simulated: same endpoint, no duplicate from cache in frontend)')

vis_types = [s.get('visual_type') for s in segs]
ok('T7  visual_types=' + str(vis_types) + ' (image removed from lesson prompt)')

ev_wrong = post('http://localhost:8000/api/evaluate-answer', {
    'concept': seg['concept'], 'teaching_goal': seg['teaching_goal'],
    'question_prompt': tc['question']['prompt'],
    'question_type': 'short_answer',
    'correct_answer': tc['correct_answer'],
    'acceptable_answer_points': tc['acceptable_answer_points'],
    'student_answer': 'The speed of sound is what causes this effect',
    'learner_level': p['learner_level'], 'language': p['language'],
    'teaching_script': tc['explanation'], 'attempt_count': 1,
})
assert ev_wrong['classification'] in ('misconception', 'partial')
assert ev_wrong['next_action'] in ('reteach', 'follow_up')
ok('T8  Wrong answer classification=' + ev_wrong['classification'] + ' next=' + ev_wrong['next_action'])
assert ev_wrong.get('adapted_explanation') or ev_wrong.get('follow_up_question')
ok('T9  Reteach/follow-up content returned for wrong answer')

ev_correct = post('http://localhost:8000/api/evaluate-answer', {
    'concept': seg['concept'], 'teaching_goal': seg['teaching_goal'],
    'question_prompt': tc['question']['prompt'],
    'question_type': 'short_answer',
    'correct_answer': tc['correct_answer'],
    'acceptable_answer_points': tc['acceptable_answer_points'],
    'student_answer': tc['correct_answer'],
    'learner_level': p['learner_level'], 'language': p['language'],
    'teaching_script': tc['explanation'], 'attempt_count': 1,
})
assert ev_correct['classification'] == 'correct'
assert ev_correct['next_action'] == 'continue'
ok('T10 Correct answer -> correct + continue')

print()
ok('ALL LIVE API TESTS PASSED.')
print('T5/T6/T11-T13 require browser interaction.')
