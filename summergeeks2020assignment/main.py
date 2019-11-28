import smtplib, ssl
import os,sys
import qdarkstyle
import configparser
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets,QtSql
from UI import Ui_MainWindow
import way2smsApi
class Main_Win(Ui_MainWindow):
    def setupUi(self,MainWindow):
        Ui_MainWindow.setupUi(self,MainWindow)
        
        self.sms_APIKEY="YOUR-API_KEY"
        self.sms_SECRET="YOUR-SECRET-KEY"
        self.sms_SENDERID="YOUR-SENDER-ID"

        self.Email_port = 587
        self.Email_smtp_server = "YOUR-SMTP-ADDRESS"   #smtp.gmail.com for GMAIL
        self.Email_sender_email = "YOUR-EMAIL_ADDRESS" 
        self.Email_sender_pass = "YOUR-EMAIL-PASSWORD"


        phoneregex=QtCore.QRegExp("^(?:(?:\+|0{0,2})91(\s*[\ -]\s*)?|[0]?)?[6789]\d{9}|(\d[ -]?){10}\d$")
        self.phone_validator=QtGui.QRegExpValidator()
        self.phone_validator.setRegExp(phoneregex)
        emailregex=QtCore.QRegExp("\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b")
        emailregex.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.email_validator=QtGui.QRegExpValidator()
        self.email_validator.setRegExp(emailregex)
        
        self.vPhone.setValidator(self.phone_validator)
        self.hPhone.setValidator(self.phone_validator)
        self.vEmail.setValidator(self.email_validator)
        self.hEmail.setValidator(self.email_validator)

        self.submitbutton.clicked.connect(self.notifyHost)

        self.visitorsTable=QtSql.QSqlTableModel(MainWindow)
        self.visitorsTable.setTable("visitors")
        self.visitorInsideView.setModel(self.visitorsTable)
        self.visitorsTable.setFilter("checkout is NULL or checkout is ''")
        self.visitorsTable.setHeaderData(0,QtCore.Qt.Horizontal,"Visitor Name",QtCore.Qt.DisplayRole)
        self.visitorsTable.setHeaderData(1,QtCore.Qt.Horizontal,"Visitor Email",QtCore.Qt.DisplayRole)
        self.visitorsTable.setHeaderData(2,QtCore.Qt.Horizontal,"Visitor Phone No.",QtCore.Qt.DisplayRole)
        self.visitorsTable.setHeaderData(3,QtCore.Qt.Horizontal,"Host Name",QtCore.Qt.DisplayRole)
        self.visitorsTable.setHeaderData(4,QtCore.Qt.Horizontal,"Host Email",QtCore.Qt.DisplayRole)
        self.visitorsTable.setHeaderData(5,QtCore.Qt.Horizontal,"Host Phone No.",QtCore.Qt.DisplayRole)
        self.visitorsTable.setHeaderData(6,QtCore.Qt.Horizontal,"Check In Time",QtCore.Qt.DisplayRole)
        self.visitorInsideView.hideColumn(7)
        self.visitorInsideView.resizeColumnsToContents()
        self.visitorsTable.select()
        self.tabWidget.currentChanged.connect(self.visitorsTable.select)

        self.visitorInsideView.doubleClicked.connect(self.checkOutBtn.click)
        self.checkOutBtn.clicked.connect(self.checkOutAndNotify)

        def endProgram():
            MainWindow.close()
        
        self.actionExit.triggered.connect(endProgram)

    def clearForm(self):
        self.hEmail.clear()
        self.hName.clear()
        self.hPhone.clear()
        self.vEmail.clear()
        self.vName.clear()
        self.vPhone.clear()

    def checkOutAndNotify(self):
        CurrRec=self.visitorsTable.record(self.visitorInsideView.currentIndex().row())
        checkOutTime=datetime.now()
        query=QtSql.QSqlQuery()
        query.prepare("update visitors set checkout=:chotime where checkin=:chin")
        query.addBindValue(checkOutTime.strftime("%Y-%m-%d %H:%M:%S"))
        query.addBindValue(CurrRec.value("checkin"))
        query.exec_()
        self.visitorsTable.select()
        #Notification
        visitorMessage=f"""
Visit Details:
Name - {CurrRec.value("vname")}
Phone - {CurrRec.value("vphone")}
Check-in Time - {datetime.strptime(CurrRec.value("checkin"),"%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")}
Check-Out Time - {checkOutTime.strftime('%I:%M %p')}
Host - {CurrRec.value("hname")}
Address - {CurrRec.value("hemail")}
"""
        #print(visitorMessage)
        self.server=smtplib.SMTP(self.Email_smtp_server, self.Email_port)
        self.server.starttls()
        self.server.login(self.Email_sender_email, self.Email_sender_pass)
        self.server.sendmail(self.Email_sender_email,CurrRec.value("vemail"),visitorMessage)
        self.server.quit()


    def notifyHost(self):
        if self.vEmail.text()=="" or self.vName.text()=="" or self.vPhone.text()=="" or self.hEmail.text()=="" or self.hName.text()=="" or self.hPhone.text()=="":
            return
        query=QtSql.QSqlQuery()
        query.prepare("insert into visitors (vname,vemail,vphone,hname,hemail,hphone,checkin) values(:vn,:ve,:vp,:hn,:he,:hp,:chin)")
        query.addBindValue(self.vName.text())
        query.addBindValue(self.vEmail.text())
        query.addBindValue(self.vPhone.text())
        query.addBindValue(self.hName.text())
        query.addBindValue(self.hEmail.text())
        query.addBindValue(self.hPhone.text())
        Checkin=datetime.now()
        query.addBindValue(Checkin.strftime("%Y-%m-%d %H:%M:%S"))
        query.exec_()
        if query.numRowsAffected():
            hostMsg=f"""
Visitor Details:
Name - {self.vName.text()}
Email - {self.vEmail.text()}
Phone - {self.vPhone.text()}
Checkin Time - {Checkin.strftime("%I:%M %p")}
"""
            #print(hostMsg)
            response = way2smsApi.sendPostRequest(way2smsApi.URL, self.sms_APIKEY, self.sms_SECRET, 'prod', self.hPhone.text(), self.sms_SENDERID, hostMsg )
            print(response.text)
            self.server=smtplib.SMTP(self.Email_smtp_server, self.Email_port)
            self.server.starttls()
            self.server.login(self.Email_sender_email, self.Email_sender_pass)
            self.server.sendmail(self.Email_sender_email,self.hEmail.text(),hostMsg)
            self.server.quit()
            self.clearForm()
        else:
            print(query.lastError().text())
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    db=QtSql.QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName('visitors')
    if db.open():
        MainWindow=QtWidgets.QMainWindow()
        ui=Main_Win()
        ui.setupUi(MainWindow)
        qry=QtSql.QSqlQuery()
        qry.exec_("create table if not exists visitors(vname varchar(30), vemail varchar(50), vphone int(10),"
            "hname varchar(30), hemail varchar(50), hphone int(10),"
            "checkin DEFAULT CURRENT_TIMESTAMP, checkout DATETIME"
        ")")
        
        MainWindow.show()
        sys.exit(app.exec_())