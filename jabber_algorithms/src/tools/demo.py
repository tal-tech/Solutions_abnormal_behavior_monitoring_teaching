from jabberTool import jabberClassifier

if __name__=="__main__":
    jab = jabberClassifier()
    with open('./test.json','r') as f:
        word = f.read()
    result = jab.predict_one_course(word)
    print(result)

