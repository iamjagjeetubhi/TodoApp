from sendsms.backends.base import BaseSmsBackend
import urllib.parse
import urllib.request

def sms(phone, text):
    usr = "3881"
    pwd = "tccBS"
    text = urllib.parse.quote(text)
    values = "?usr={usr}&pwd={pwd}&ph={ph}&text={text}".format(usr=usr, pwd=pwd, ph=phone, text=text)
    url = "http://103.27.87.89/send.php"+values
    resp = urllib.request.urlopen(url)
    respData = resp.read()
    return respData

class AwesomeSmsBackend(BaseSmsBackend):

    def send_messages(self, messages):
        for message in messages:
            for to in message.to:
                try:
                    sms(to, message.body)
                except:
                    if not self.fail_silently:
                        raise