import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time


def start_quiz(questions):
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 620)
    detector = HandDetector(detectionCon=0.8)
    score = 0

    class MCQ():
        def __init__(self, q):
            self.question = q.title
            self.choice1 = q.op1
            self.choice2 = q.op2
            self.choice3 = q.op3
            self.choice4 = q.op4
            self.answer = q.ans
            self.userAns = None

        def update(self, cursor, bboxs):

            for x, bbox in enumerate(bboxs):
                x1, y1, x2, y2 = bbox
                if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                    if x == 0:
                        self.userAns = self.choice1
                    if x == 1:
                        self.userAns = self.choice2
                    if x == 2:
                        self.userAns = self.choice3
                    if x == 3:
                        self.userAns = self.choice4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
                    print('ans',self.userAns, 'x=',x)


    # # Import csv file data
    # pathCSV = "Mcqs.csv"
    # with open(pathCSV, newline='\n') as f:
    #     reader = csv.reader(f)
    #     dataAll = list(reader)[1:]

    # Create Object for each MCQ
    mcqList = []
    for q in list(questions):
        mcqList.append(MCQ(q))

    print("Total MCQ Objects Created:", len(mcqList))

    qNo = 0
    qTotal = len(list(questions))

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        if qNo < qTotal:
            mcq = mcqList[qNo]
            img, bbox = cvzone.putTextRect(img, mcq.question, [100, 100], 2, 2, offset=40, border=2,colorR=(255,0,0))
            img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [100, 250], 2, 2, offset=40, border=2,colorR=(255,0,0))
            img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [400, 250], 2, 2, offset=40, border=2,colorR=(255,0,0))
            img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [100, 400], 2, 2, offset=40, border=2,colorR=(255,0,0))
            img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [400, 400], 2, 2, offset=40, border=2,colorR=(255,0,0))

            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8]
                length, info,img = detector.findDistance(lmList[8], lmList[12],img)
                print(length)
                if length < 35:
                    mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                    if mcq.userAns is not None:
                        time.sleep(.5)
                        qNo += 1
        else:
            score = 0
            for mcq in mcqList:
                if mcq.answer == mcq.userAns:
                    score += 1
            score = round((score / qTotal) * 100, 2)
            img, _ = cvzone.putTextRect(img, "Quiz Completed", [250, 300], 2, 2, offset=50, border=3)
            img, _ = cvzone.putTextRect(img, f'Your Score: {score}%', [700, 300], 2, 2, offset=50, border=3)
            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8]
                length, info,img = detector.findDistance(lmList[8], lmList[12],img)
                if length < 35:
                    break


        # Draw Progress Bar
        barValue = 150 + (950 // qTotal) * qNo
        cv2.rectangle(img, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
        cv2.rectangle(img, (150, 600), (1100, 650), (0, 0, 0), 5)
        img, _ = cvzone.putTextRect(img, f'{round((qNo / qTotal) * 100)}%', [1130, 635], 2, 2, offset=16)

        cv2.imshow("Img", img)
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    return score

    


if __name__ == "__main__":
    from database import Question
    from sqlalchemy.engine import create_engine
    from sqlalchemy.orm import sessionmaker

    def opendb():
        engine = create_engine("sqlite:///db.sqlite")
        Session = sessionmaker(bind=engine)
        return Session()

    db = opendb()
    questions = db.query(Question).filter(Question.category=='GK')
    score = start_quiz(questions)
    print("score",score)
