import unittest


from ml.features.preprocessing import calc_target, calc_indicators
import yfinance as yf
class StockDataProcessingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Laden Sie ein kleines Datenbeispiel herunter, das für alle Tests verwendet wird
        cls.sample_data = yf.download("AAPL", start="2019-01-01", end="2020-01-10")

    def test_calc_target(self):
        df = calc_target(self.sample_data.copy())
        # Prüfen Sie, ob die 'Target'-Spalte hinzugefügt wurde
        self.assertIn('Target', df.columns)
        # Fügen Sie weitere Überprüfungen hinzu, z.B. Datentypen oder erwartete Werte

    def test_calc_indicators(self):
        df = calc_indicators(self.sample_data.copy())
        # Prüfen Sie, ob die Indikatorenspalten hinzugefügt wurden
        self.assertIn('SMA 10', df.columns)
        # Weitere Tests für andere Indikatoren

    def test_scaling(self):
        df = calc_target(self.sample_data.copy())
        df = calc_indicators(df)
        neu = df.copy()
        df_scaled = scaling(df)

        self.assertNotEqual(neu['Close'].mean(), df_scaled['Close'].mean())  # Überprüfen, ob der DataFrame skaliert wurde

    def test_get_data(self):
        # Simulieren Sie den get_data-Aufruf (kann komplex sein, abhängig von den Abhängigkeiten in der Funktion)
        # Stellen Sie sicher, dass alle Teile der Funktion wie erwartet arbeiten
        pass

if __name__ == '__main__':
    unittest.main()


