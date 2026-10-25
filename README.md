# antenna-generator

Tento repozitář obsahuje Python skripty pro generování anténových návrhů ve formátu KiCad PCB.

## Obsah
- `test.py` — generuje kruhovou anténu s mezerou pro přívod
- `test1.py` — generuje spirálovou anténu

## Použití

### Kruhová anténa
```powershell
py .\test.py --min-diameter 20 --trace-width 0.3 --gap 0.2 --rings 6 --feed-gap-deg 30 --feed-angle-deg 90
```

### Spirálová anténa
```powershell
py .\test1.py --outer-radius 20 --track-width 0.6 --turns 6 --center-x 60 --center-y 60
```

## Výstupy
- `ring_antenna.kicad_pcb`
- `spiral_antenna.kicad_pcb`

## Poznámka
Skripty jsou navrženy pro použití v systému Windows a pro otevření v KiCad PCB Editor.
