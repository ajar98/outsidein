import json, operator
from watson_developer_cloud import AlchemyLanguageV1 as AlchemyLanguage
from watson_developer_cloud.tone_analyzer_v3 import ToneAnalyzerV3

ALCHEMY_API_KEY = 'bee64efa9bf4e1192177e2993b62615c338ba8fb'

TONE_ANALYZER_USER = 'f378166c-4ea2-4487-ae8a-6b0007b267b4'
TONE_ANALYZER_PASS = 'f6BHihiDbguw'

def get_text_sentiment_score(text):
    alchemy_language = AlchemyLanguage(api_key=ALCHEMY_API_KEY)
    result = alchemy_language.sentiment(text=text)
    if result['docSentiment']['type'] == 'neutral':
        return 'neutral', 0
    return result['docSentiment']['type'], result['docSentiment']['score']

def get_text_sentiment(text):
    ta = ToneAnalyzerV3(
            '2016-05-19',
            username=TONE_ANALYZER_USER,
            password=TONE_ANALYZER_PASS
    )
    response = ta.tone(text)
    # print(response)
    if 'sentences_tone' in response:
        text_responses = response['sentences_tone']
    else:
        text_responses = [response['document_tone']]
    emotion_responses = []
    for text_response in text_responses:
        emotion_response = dict()
        if 'text' in text_response:
            emotion_response['text'] = text_response['text']
        else:
            emotion_response['text'] = text
        emotion_tone = text_response['tone_categories'][0]
        emotions = {e['tone_name']: e['score'] for e in emotion_tone['tones']}
        emotion_response['emotions'] = emotions
        emotion_responses.append(emotion_response)
    return emotion_responses

def avg_sentiment(sentiment_response):
    return {
        'Anger': categories(sentiment_response, 'Anger'),
        'Disgust': categories(sentiment_response, 'Disgust'),
        'Sadness': categories(sentiment_response, 'Sadness'),
        'Fear': categories(sentiment_response, 'Fear'),
        'Joy': categories(sentiment_response, 'Joy')
    }

def categories(sentiment_response, text):
    added = 0
    for i in range(len(sentiment_response)):
        added += sentiment_response[i]['emotions'][text]
    return added/len(sentiment_response)

def max_sentiment(sentiment_response):
    max_value = -1
    max_emotion = ""
    max_sentence = ""
    for sentence in sentiment_response:
        temp = max(sentence['emotions'].items(), key=operator.itemgetter(1))
        if temp[1] > max_value:
            max_emotion, max_value, max_sentence = temp[0], temp[1], sentence['text']
    return max_sentence, max_emotion, max_value

if __name__ == '__main__':
    text = input('Enter the recent happening from the day and your feelings: ')
    score = get_text_sentiment_score(text)
    resp = get_text_sentiment(text)
    print(max_sentiment(resp))
    print(avg_sentiment(resp))
    print(score)
