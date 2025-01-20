from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class MySeleniumTests(StaticLiveServerTestCas):
    # no crearem una BD de test en aquesta ocasió (comentem la línia)
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
	opts = Options()
	cls.selenium = WebDriver(options=opts)
	cls.selenium.implicity_wait(5)
	# creem superusuari
	user = Uer.objects.create_user("isard", "isard@iardvdi.com", "pirineus")
	user.is_superuser = True
	user.is_staff = True
	user.save()

    @classmethod
    def test_element_not_present(self):
	self.selenium.get(f"{self.live_server_url}/admin/")
	try:
	    self.selenium.find_element(By.XPATH, "//a[text()='Log out']")
	    assert False, "Trobat element que NO hi ha de ser"
	except NoSuchElementException:
	    pass
