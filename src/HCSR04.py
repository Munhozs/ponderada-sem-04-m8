import machine, time
from machine import Pin
from time import sleep

class SensorUltrassonicoHCSR04:
    # echo_timeout_us é baseado no limite de alcance do chip (150cm)
    def __init__(self, pino_trigger, pino_echo, echo_timeout_us=500*2*30):
        """
        pino_trigger: Pino de saída para enviar pulsos
        pino_echo: Pino de leitura para medir a distância. O pino deve ser protegido com um resistor de 1k
        echo_timeout_us: Tempo limite em microssegundos para escutar o pino echo.
        Por padrão, é baseado no alcance limite do sensor (1,5m)
        """
        self.echo_timeout_us = echo_timeout_us
        # Inicializa o pino de trigger (saída)
        self.trigger = Pin(pino_trigger, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Inicializa o pino de echo (entrada)
        self.echo = Pin(pino_echo, mode=Pin.IN, pull=None)

    def _enviar_pulso_e_aguardar(self):
        """
        Envia o pulso para o trigger e escuta no pino echo.
        Utilizamos o método `machine.time_pulse_us()` para obter os microssegundos até que o eco seja recebido.
        """
        self.trigger.value(0)  # Estabiliza o sensor
        time.sleep_us(5)
        self.trigger.value(1)
        # Envia um pulso de 10us.
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            tempo_pulso = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return tempo_pulso
        except OSError as ex:
            if ex.args[0] == 110:  # 110 = ETIMEDOUT
                raise OSError('Fora de alcance')
            raise ex

    def distancia_cm(self):
        """
        Obtém a distância em centímetros com operações de ponto flutuante.
        Retorna um número de ponto flutuante.
        """
        tempo_pulso = self._enviar_pulso_e_aguardar()

        # Para calcular a distância, pegamos o tempo_pulso e dividimos por 2
        # (o pulso percorre a distância duas vezes) e por 29,1 porque
        # a velocidade do som no ar (343,2 m/s), que é equivalente a
        # 0,034320 cm/us, o que significa 1cm a cada 29,1us
        cms = (tempo_pulso / 2) / 29.1
        return cms

# Configuração do sensor com os pinos apropriados e tempo limite de eco específico
sensor_ultrassonico = SensorUltrassonicoHCSR04(pino_trigger=2, pino_echo=3, echo_timeout_us=10000)

while True:
    distancia = sensor_ultrassonico.distancia_cm()
    print('Distância:', distancia, 'cm')
    sleep(0.1)
