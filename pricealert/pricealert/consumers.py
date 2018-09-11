from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    Group("user-{}".format(message.user.id)).add(message.reply_channel)

@channel_session_user
def ws_message(message):
    Group("user-{}".format(message.user.id)).send({
        "text": "[user id: %s] %s" % (message.user.id, message.content['text']),
    })

@channel_session_user
def ws_disconnect(message):
    Group("user-{}".format(message.user.id)).discard(message.reply_channel)
