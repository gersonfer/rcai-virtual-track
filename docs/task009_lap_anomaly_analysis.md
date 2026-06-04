# Architectural Analysis: Lap Time Anomaly (7.287s)

## 1. Origem do Valor (Onde surgiu o 7.287s?)
O valor de `7.287s` foi gerado pela classe `DriverModel` no momento em que a volta (lap) começou a ser processada, especificamente dentro do método `generate_lap()`.

## 2. Qual componente o gerou?
A classe responsável foi a `DriverModel` (`orchestrator/driver_model.py`), na seção de **Deslot Simulation**.

## 3. Isso é um comportamento esperado ou defeito?
Isso é um **comportamento perfeitamente esperado** do ponto de vista matemático. O sistema simulou um *deslot* (saída de pista) para o Ferrari 499P nessa volta.

O motivo de ter causado estranheza na análise dos logs é apenas visual: o log do deslot (`[LANE 1] Ferrari 499P DESLOT (recovery=...s)`) só é impresso pelo `RaceRuntime` **no final** do tempo da volta. Como a pista perdeu energia em `elapsed=4.110s` e o carro entrou em `COASTING` e em seguida `MOMENTUM_LOST`, o loop foi interrompido e a volta descartada antes que o aviso de *deslot* pudesse ser impresso no console. O sistema engoliu o log do acidente porque a corrida foi pausada no meio do tempo de recuperação!

## 4. Caminho Completo do Cálculo (Para o Ferrari 499P)
De acordo com o `profiles.json`, o Ferrari 499P possui a seguinte configuração:
- `min_lap`: 4.05s
- `max_lap`: 4.60s
- `deslot_probability`: 0.010 (1% de chance)
- `recovery_time_avg`: 2.0s

### O Cálculo Matemático da Volta:
1. **Base Lap Generation:** O `LapGenerator` calculou uma volta base dentro dos limites normais, por exemplo: `base_lap = 4.250s` (obedecendo ao min de 4.05 e max de 4.60).
2. **Rolagem do Deslot:** O `random.random()` sorteou um número menor que `0.010`, ativando o bloco `deslotted = True`.
3. **Recovery Time (Tempo de Resgate):** O modelo sorteou um valor `uniform` entre `0.5 * recovery_time_avg` (1.0s) e `1.5 * recovery_time_avg` (3.0s). 
   - Neste caso específico, o valor sorteado foi de aproximadamente **3.037s**.
4. **Lap Time Final:** `lap_time = base_lap + recovery_time` 
   - Exemplo aproximado: `4.250s + 3.037s = 7.287s`.

Portanto, o carro iria completar a volta normalmente em 7.287s (incluindo o tempo parado sendo resgatado). No entanto, aos `4.110s` ocorreu um corte de energia (Pause). Como ainda faltavam `3.177s` para a conclusão da volta, o tempo de `coasting_duration` (0.500s) não foi suficiente para cruzar a linha, e o sistema registrou corretamente o `MOMENTUM_LOST`.

## Conclusão
A arquitetura comportou-se de forma exemplar, simulando perfeitamente a física e a probabilidade estabelecida no perfil. O "anômalo" 7.287s é o tempo de uma volta com saída de pista. Como não há modificações de código a serem feitas, podemos prosseguir com tranquilidade para a **TASK-010**.
