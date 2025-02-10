import time
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class MySeleniumTests(StaticLiveServerTestCase):
    # no crearem una BD de test en aquesta ocasió (comentem la línia)
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # creem superusuari
        user = User.objects.create_user("isard", "isard@iardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_user_in_list_but_cannot_login(self):
        # iniciem sessió com a superusuari
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        time.sleep(2)
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(2)

        # creem un usuari normal sense permissos
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
        self.selenium.find_element(By.NAME, "username").send_keys("usuari_normal")
        self.selenium.find_element(By.NAME, "password1").send_keys("test_password_1234")
        self.selenium.find_element(By.NAME, "password2").send_keys("test_password_1234")
        time.sleep(2)
        self.selenium.find_element(By.NAME, "_save").click()
        time.sleep(2)

        # anem a la pàgina de llista d'usuaris
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")
        time.sleep(2)

        # comprovem que l'usuari creat està a la llista
        user_found = False
        row = 1
        while True:
            try:
                xpath = f"/html/body/div/div/main/div/div/div/div/form/div[2]/table/tbody/tr[{row}]/th/a"
                element = self.selenium.find_element(By.XPATH, xpath)
                if "usuari_normal" in element.text:
                    user_found = True
                    break
                row += 1
            except NoSuchElementException:
                break

        if not user_found:
            print("L'usuari no es troba a la llista d'usuaris")
        time.sleep(2)

        # tanquem la sessió del superusuari
        #self.selenium.get(f"{self.live_server_url}/admin/logout/")
        self.selenium.find_element(By.XPATH, "//button[text()='Log out']").click()
        time.sleep(2)

        # intentem iniciar sessió com a usuari normal
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("usuari_normal")
        self.selenium.find_element(By.NAME, "password").send_keys("test_password_1234")
        time.sleep(2)
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(2)

        # comprovem que no pot accedir (ha de mantenir-se a la pàgina de login amb error)
        error_message = self.selenium.find_element(By.CLASS_NAME, "errornote").text
        assert "Please enter the correct" in error_message, "L'usuari normal ha pogut accedir a l'admin i no hauria de poder"
