import json
from flask import Flask, request, make_response, render_template

from wit_module import CallWit

witObject = CallWit()

app = Flask(__name__)

@app.route("/listening", methods=["GET"])
def hears():

    return "Connected"
#     """
#     This route listens for incoming events from Slack and uses the event
#     handler helper function to route events to our Bot.
#     """
#     print (request.data)
#     slack_event = json.loads(request.data)
#
#     # slack_event = request.data
#     print slack_event
#
#     # ============= Slack URL Verification ============ #
#     # In order to verify the url of our endpoint, Slack will send a challenge
#     # token in a request and check for this token in the response our endpoint
#     # sends back.
#     #       For more info: https://api.slack.com/events/url_verification
#     if "challenge" in slack_event:
#         return make_response(slack_event["challenge"], 200, {"content_type":
#                                                              "application/json"
#                                                              })
#
#     # ============ Slack Token Verification =========== #
#     # We can verify the request is coming from Slack by checking that the
#     # verification token in the request matches our app's settings
#     if witObject.SLACK_VERIFY_TOKEN != slack_event.get("token"):
#         message = "Invalid Slack verification token: %s \npyBot has: \
#                    %s\n\n" % (slack_event["token"], witObject.SLACK_VERIFY_TOKEN)
#         # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
#         # Slack's automatic retries during development.
#         make_response(message, 403, {"X-Slack-No-Retry": 1})
#
# @app.route("/listening", methods=["POST"])
def activate_slack():
    witObject.run()

if __name__=='__main__':
    app.run(debug=True)
