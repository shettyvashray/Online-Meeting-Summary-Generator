from django.shortcuts import render
from django.http import HttpResponse
import json
from reportlab.pdfgen import canvas  
from django.template.response import TemplateResponse

import moviepy.editor
from tkinter.filedialog import *

# summarytext = ""

# Create your views here.
def Landing_page(request):
    return render(request,'blank.html')

def simple_function(request):
    video = askopenfilename()
    video = moviepy.editor.VideoFileClip(video)
    audio = video.audio

    audio.write_audiofile("sample.mp3")
    print("Converted to mp3")


    from google.cloud import speech

    client = speech.SpeechClient.from_service_account_file('key.json')

    file_name = "sample.mp3"

    with open(file_name, 'rb') as f:
        mp3_data = f.read()

    audio_file = speech.RecognitionAudio(content=mp3_data)

    config = speech.RecognitionConfig(
        sample_rate_hertz=48000,
        language_code="en",
        enable_automatic_punctuation = True
    )

    response = client.recognize(config=config, audio=audio_file)

    # print(response)

    for result in response.results:
        final = "{}".format(result.alternatives[0].transcript)

    print(final)



    '''
    NLTK MODEL CODE
    '''

    # Tokenizing Sentences
    from nltk.tokenize import sent_tokenize

    # Tokenizing Words
    from nltk.tokenize import word_tokenize
    import nltk
    from string import punctuation
    from nltk.corpus import stopwords
    nltk.download('stopwords')
    nltk.download('punkt')

    # Cleaning text that is got from meet transcript
    def clean(text):
        sample = text.split('**')
        sample.pop(0)
        clean_text = ""
        i = 0
        for t in sample:
            if i % 2 != 0:
                clean_text += str(t)
            i += 1
        return clean_text


    # Finding list of stopwords ( Stopwords are
    # those which do not add meaning to sentence)
    stop_words = set(stopwords.words("english"))

    # Tokenize
    def Wtokenize(text):
        words = word_tokenize(text)
        return words


    # Frequency table will be storing frequency of each word
    # appearing in input text after removing stop words
    # Need: It will be used for finding most relevant sentences
    # as we will be applying this dictionary on every sentence
    # and find its importance over other
    def gen_freq_table(text):
        freqTable = dict()
        words = Wtokenize(text)
        
        for word in words:
            word = word.lower()
            if word in stop_words:
                continue
            if word in freqTable:
                freqTable[word] += 1
            else:
                freqTable[word] = 1
        return freqTable

    # Sentence Tokenize
    def Stokenize(text):
        sentences = sent_tokenize(text)
        return sentences

    # Storing Sentence Scores
    def gen_rank_sentences_table(text):

        # dictionary storing value for each sentence
        sentenceValue = dict()
        
        # Calling function gen_freq_table to get frequency
        # of words
        freqTable = gen_freq_table(text)
        
        # Calling list of sentences after tokenization
        sentences = Stokenize(text)

        for sentence in sentences:
            for word, freq in freqTable.items():
                if word in sentence.lower():
                    if sentence in sentenceValue:
                        sentenceValue[sentence] += freq
                    else:
                        sentenceValue[sentence] = freq
        return sentenceValue


    def summary(text):
        sum = 0
        sentenceValue = gen_rank_sentences_table(text)
        for sentence in sentenceValue:
            sum += sentenceValue[sentence]
        avg = int(sum / len(sentenceValue))
        summary = ""
        sentences = Stokenize(text)
        for sentence in sentences:
            if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * avg)):
                summary += " " + sentence
        return summary


    def mainFunc(inp_text):

        # getting text cleaned
        if("**" not in inp_text):
            text = inp_text
        else:
            cleaned_text = clean(inp_text)
            text = cleaned_text
        global summary_text
        summary_text = summary(text)
        print("\nModel Summary: ", summary_text)

        return summary_text

    mainFunc(final)
 
    return HttpResponse("""<html><script>window.location.replace('/');</script></html>""")

def output(request):
    return render(request, "output.html", {'text':summary_text})

def getpdf(request):  
    response = HttpResponse(content_type='application/pdf')  
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'  
    p = canvas.Canvas(response)  
    p.setFont("Times-Roman", 15)

    # p.drawString(100,700, summary_text) 
    text = p.beginText(40,680)
    text.setFont("Times-Roman", 15)
    for line in summary_text:
        text.textLine(line)

    p.drawText(text)

    p.showPage()  
    p.save()  
    return response  