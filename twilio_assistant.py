from __future__ import print_function
import json
from flask import Flask, jsonify, render_template, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from watson_developer_cloud import AssistantV2
from secret.keys import *

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/assistant", methods = ['POST'])
def assistant():
    """End point dedicated to communicate with the user as assistant"""
    welcome_message = 'Wellcome to the Assistant voice platform, how can I help you?'
    message = ''
    number = ''
    twilio_number = ''

    assistant = AssistantV2(
        username=username,
        password=password,
        url=url,
        version=version)

    if request.values.get('SpeechResult'):
        print(message)
        message = request.values['SpeechResult']

    if request.values.get('From'):
        number = request.values['From']

    if request.values.get('To'):
        twilio_number = request.values['To']  


    twilio_response = VoiceResponse()
    gather = Gather(input='speech', action='/assistant', speechTimeout='auto')

    if message != '':
        session = assistant.create_session(assistanceID).get_result()
        sessionID = session['session_id']

        message = assistant.message(
            assistanceID,
            sessionID,
            input={'text': message}).get_result()
    
        print(json.dumps(message, indent=2))

        if (len(message['output']['generic']) > 0):
            for intern_response in message['output']['generic'] :
                if intern_response['response_type'] == 'text':
                    gather.say(intern_response['text'], voice= 'alice')

    else:
        print(welcome_message)
        gather.say(welcome_message, voice= 'alice');

    twilio_response.append(gather)

    return str(twilio_response)


if __name__ == '__main__':
    app.run(debug=True)