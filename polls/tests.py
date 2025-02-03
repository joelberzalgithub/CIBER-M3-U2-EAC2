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

        """
        cls.selenium.get(f"{cls.live_server_url}/admin/login/")
        cls.selenium.find_element(By.NAME, "username").send_keys("isard")
        cls.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        cls.selenium.find_element(By.XPATH, "//input[@type='submit']").click()
        """

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_user_in_list_but_cannot_login(self):
        # creem un usuari normal sense permissos
        user = User.objects.create_user(username="usuari_normal", password="test1234")
        user.is_superuser = False
        user.is_staff = False
        user.save()

        # iniciem sessió com a superusuari per veure la llista d'usuaris
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()

        # anem a la pàgina de llista d'usuaris
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")

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

        # tanquem la sessió del superusuari
        #self.selenium.get(f"{self.live_server_url}/admin/logout/")
        self.selenium.find_element(By.XPATH, "//button[text()='Log out']").click()

        # intentem iniciar sessió com a usuari normal
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("usuari_normal")
        self.selenium.find_element(By.NAME, "password").send_keys("test1234")
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()

        """
        # comprovem que no pot accedir (ha de mantenir-se a la pàgina de login amb error)
        error_message = self.selenium.find_element(By.CLASS_NAME, "errornote").text
        assert "Please enter the correct" in error_message, "L'usuari normal ha pogut accedir a l'admin i no hauria de poder"
        """

    """
    def test_element_not_present(self):
        self.selenium.get(f"{self.live_server_url}/admin/")
        try:
            self.selenium.find_element(By.XPATH, "//a[text()='Log out']")
            assert False, "Trobat element que NO hi ha de ser"
        except NoSuchElementException:
            pass
    """
