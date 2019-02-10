from __future__ import print_function
import json
from flask import Flask, jsonify, render_template, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from watson_developer_cloud import AssistantV2
from assistant_config.config import *
from functions.functions import *

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

sessionID = ""

#################################################
# Flask Routes
#################################################
@app.route("/assistant", methods = ['POST'])
def assistant():
    """End point dedicated to communicate with the user as assistant 'Yelp Voice'"""
    
    message = ''
    number = ''
    twilio_number = ''
    global sessionID

    assistant = AssistantV2(
        username=watson_username,
        password=watson_password,
        url=watson_url,
        version=watson_version)

    if request.values.get('SpeechResult'):
        print(message)
        message = request.values['SpeechResult']

    if request.values.get('From'):
        number = request.values['From']

    if request.values.get('To'):
        twilio_number = request.values['To']  

    twilio_response = VoiceResponse()
    gather = Gather(input='speech', action='/assistant', speechTimeout='auto')

    # print(sessionID)

    if sessionID == "":
        session = assistant.create_session(watson_assistanceID).get_result()
        sessionID = session['session_id']

    print("message: {}".format(message))

    if message != '':

        watson_call = assistant.message(
            watson_assistanceID,
            sessionID,
            options={
                'return_context': 'true'
            },
            input={'text': message})
            
        response_watson = watson_call.get_result()

        print(json.dumps(response_watson, indent=1))

        if (len(response_watson['output']['generic']) > 0):
            for intern_response in response_watson['output']['generic'] :
                if intern_response['response_type'] == 'text':
                    print(intern_response['text'])

                    # if intern_response['text'] == "{userName}":
                    #     messageApi = assistant.message(
                    #         watson_assistanceID,
                    #         sessionID,
                    #         input={'text': login()}).get_result()

                    #     if (len(messageApi['output']['generic']) > 0):
                    #         for intern_api_response in messageApi['output']['generic'] :
                    #             if intern_api_response['response_type'] == 'text':
                    #                 print(intern_api_response['text'])
                    #                 gather.say(intern_api_response['text'], voice= 'alice')

                    if intern_response['text'] == "{restaurant}":
                        gather.say('sure, I will let you know about the some restaurants nearby', voice= 'alice')

                        for idea_response  in getRestaurantList() :
                            gather.say(idea_response, voice= 'alice')

                    elif intern_response['text'] == "{resumeviewed}":
                        gather.say('sure thing, I will let you know about the most recent resumes viewed.', voice= 'alice')

                        # for idea_response in most_viewed_resumes() :
                        #     gather.say(idea_response, voice= 'alice')

                    elif intern_response['text'] == "{actionused}":
                        gather.say('hold on a second, I am collecting the data.', voice= 'alice')

                        # for idea_response in actions_used_by_recruiter() :
                        #     gather.say(idea_response, voice= 'alice')

                    elif (len(response_watson['output']['intents']) > 0):

                        for intern_intent in response_watson['output']['intents'] :

                            if intern_intent["intent"] == "No" or intern_intent["intent"] == "General_Ending":
                                twilio_response.say(intern_response['text'], voice= 'alice')

                                assistant.delete_session(watson_assistanceID, sessionID)
                                sessionID = ""

                                gather.pause(2)
                                twilio_response.hangup()

                            else:
                                gather.say(intern_response['text'], voice= 'alice')

                    else:
                        gather.say(intern_response['text'], voice= 'alice')



            gather.pause(4)
            gather.say('Is there other question that I can answer?', voice= 'alice')

    else:
        response_watson = assistant.message(
            watson_assistanceID,
            sessionID,
            options={
                'return_context': 'true'
            },
            input={'text': login(number)}).get_result()

        # print(json.dumps(response_watson, indent=2))

        if (len(response_watson['output']['generic']) > 0):
            for intern_response in response_watson['output']['generic'] :
                if intern_response['response_type'] == 'text':
                    print(intern_response['text'])
                    gather.say(intern_response['text'], voice= 'alice')

            gather.pause(3)
            # print('Remember, you can know what the people is thinking about some store or business. Just ask: Yelp, let me know about Thai Restaurants.', voice= 'alice')
            gather.say('Remember, you can know what the people is thinking about some store or business. Just ask: Yelp, let me know about Thai Restaurants.', voice= 'alice')


    twilio_response.append(gather)

    # print(twilio_response)

    return str(twilio_response)


if __name__ == '__main__':
    app.run(debug=True)