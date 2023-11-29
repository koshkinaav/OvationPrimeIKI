## Документация к API OvationPrime на Python

Реализованы три метода:

- `/api/v1/draw_weighted_flux`, возвращающий картину аврорального потока частиц обрушивающихся на Землю в определенную дату, оцениваемый на основе модели OvationPrime, и имеющий следующие параметры:
  - dt: дата, в которую рассматриваются наблюдения. Формат: ```yyyy-mm-ddThh:mm:ss```
  - atype: тип частиц, для которых смотрим поток. Формат: ```string, one of [diff, mono, wave, ions]```
  - jtype: тип потока. Формат: ```string, one of [energy, number]```
  

- ```/api/v1/draw_seasonal_flux```, возвращающий картину предсказаний обнаружения той или иной частицы, согласно модели OvationPrime и имеющий следущие параметры:
  - seasonN: сезон на северном полюсе. Формат: `string, one of [winter, spring, summer, fall]`,
  - seasonS: сезон на южном плюсе. Формат: `seasonS': 'str, one of [winter, spring, summer, fall]`
  - atype: тип частиц, для которых смотрим поток. Формат: ```string, one of [diff, mono, wave, ions]```
  - jtype: тип потока. Формат: ```string, one of [energy, number]```
  

- ```/api/v1/draw_conductance```, возвращающий картину проводимости Холла и Педерсона в поределенную дату на одном из полушарий и имеющий следующие параметры:
  - dt: дата, в которую рассматриваются наблюдения. Формат: ```yyyy-mm-ddThh:mm:ss```
  - hemi: полушарие. Формат: `hemi: N or S`

## Примеры использования трех методов:
- http://193.232.6.63:8080/api/v1/draw_weighted_flux?dt=2023-11-28T10:00:00&atype=diff&jtype=energy
- http://193.232.6.63:8080/api/v1/draw_seasonal_flux?seasonN=winter&seasonS=summer&atype=diff&jtype=energy
- http://193.232.6.63:8080/api/v1/draw_conductance?dt=2023-10-28T10:00:00&hemi=N

## Примечание
**В случае некорректного посторения url, сервер возвращает в ответе подсказки. Например на ссылку:
http://193.232.6.63:8080/api/v1/draw_weighted_flux?dt=2023-11-28T10:00:00&atype=none&jtype=energy, где type=none (то есть ошиблись с типом частиц)
вернется ответ**:
```{"error":"Invalid value for atype parameter. Allowed values: diff, mono, wave, ions"}```

