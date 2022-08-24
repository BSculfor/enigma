This module is designed to mimic an enigma machine, specifically the Kriegsmarine M3/M4. [General information about the M3 enigma can be found here](https://www.cryptomuseum.com/crypto/enigma/m3/index.htm "Enigma M3, Crypto Museum.")

# Theory

The enigma machine was the primary method of sending encrypted messages from the 1920s to the 1940s, most famously by Nazi Germany during the Second World War. The enigma machine consists of three main parts: the rotors, the reflector, and the plugboard.

With each press of a key, the following process would take place, illustrated by [this diagram](https://commons.wikimedia.org/wiki/File:Enigma_wiring_kleur.svg "Enigma wiring kleur, Wikimedia."). Firstly, the rightmost rotor would turn, and possibly the other rotors. An electrical signal is then sent from the keyboard, through the plugboard, through the rotors right to left, across the reflector, back through the rotors left to right and then back through the plugboard, lighting up a light corresponding to a letter.

**Rotors (Walze)**. The key part of the enigma machine is a series of rotors which each take a letter as input and give a different letter as output. As the name "rotor" implies, each rotor turns at different times, so the overall mapping of one character to another changes for every letter of the message. The M3 comes with 5 rotors labelled with Roman numerals I to V, of which 3 can be used at a time in any order. The M4 had slots for 4 rotors in the same space as the M3, with 3 regular-sized rotors on the right and a thinner "Greek rotor" (BETA or GAMMA) in the leftmost position. The M4 also had 3 additional rotors to choose from, labelled VI, VII, and VIII. Naval rules required that one of these latter three always had to be used in an operating session.

**Ringstellung (ring setting)**. Each rotor has a rotating ring with the letters of the alphabet written on it that offsets the rotor's wiring (label 3 in [this diagram](https://en.wikipedia.org/wiki/File:Enigma_rotor_exploded_view.png "Enigma rotor exploded view, Wikipedia.")). Group-theoretically, letting P be the cycle "BCDE...  XYZA", for a rotor with wiring permutation W and ring set to the n^th letter of the alphabet (with "A" being n = 0), the permutation is P^nWP^{-n}.

**Grundstellung (ground setting)**. Users could manually set the starting positions of each rotor, denoted with a letter.

**Reflector (Umkehrwalze)**. A rotor placed to the left of the main rotors that has a self-inverse wiring, meaning that if c1 maps to c2, then c2 maps to c1. The reflector wheel doesn't have an adjustable ring and doesn't turn over. The M3 had two reflectors to choose from, labelled B and C. The M4 used thinner reflectors with the same names but with different wiring from the M3 reflectors.

**Plugboard (Steckern)**. The plugboard has a socket for each letter of the alphabet, and by attaching a wire from one socket to another swaps the corresponding letters before and after the signal has been through the rotors.

# Example usage

## Basic controls

We start by creating an instance of `Enigma`, with or without a grundstellung:

```python
>>> import enigma
>>> e = enigma.Enigma(rotors=(enigma.I, enigma.II, enigma.III), reflector=enigma.UKWB, ringstellung='AAA',
... plugboard=[], doublestep=True)
>>> m4 = enigma.Enigma(rotors=(enigma.BETA, enigma.V, enigma.VI, enigma.VIII), 
... reflector=enigma.UKWC_THIN, ringstellung='EPEL', doublestep=True, grundstellung='NAEM'
... plugboard=['AE', 'BF', 'CM', 'DQ', 'HU', 'JN', 'LX', 'PR', 'SZ', 'VW'])
```

We can encode a message using `Enigma.encode`, either explicitly specifying the grundstellung (like the first prompt below) or using the final positions from the last use (like the second prompt):

```python
>>> e.encode(message='HELLOWORLD', grundstellung='AAA')
'ILBDAAMTAZ'
>>> m4.encode('QEOB') # uses grundstellung 'NAEM', set when we instantiated m4
'CDSZ'
```

Remember that decoding is the same as encoding, so long as the same settings are used:

```python
>>> e.encode('ILBDAAMTAZ', 'AAA')
'HELLOWORLD'
>>> m4.encode('CDSZ', 'NAEM')
'QEOB'
```

The various settings can be changed by assigning to the appropriate attribute, and individual attribute values can be seen by accessing the attribute:

```python
>>> e
enigma.Enigma(rotors=(enigma.I, enigma.II, enigma.III), reflector=enigma.UKWB, 
ringstellung='AAA', grundstellung='AAA', plugboard=[], doublestep=True)
>>> e.plugboard = ['AB', 'CD']
>>> e.rotors = (enigma.III, enigma.V, enigma.I)
>>> e.reflector = enigma.UKWC
>>> e.ringstellung = 'AGA'
>>> e.grundstellung = 'DSA'
>>> e.doublestep = False
>>> e # all of the settings have been changed
enigma.Enigma(rotors=(enigma.III, enigma.V, enigma.I), reflector=enigma.UKWC, 
ringstellung='AGA', grundstellung='DSA', plugboard=['AB', 'CD'], doublestep=False)
>>> e.plugboard
['AB', 'CD']
```

## Decoding the Dönitz message

The "Dönitz message" was a message sent on 1 May 1945, announcing that Grand Admiral Karl Dönitz had been made Führer following Hitler's suicide. This example follows [this walkthrough by the Crypto Museum](https://www.cryptomuseum.com/crypto/enigma/msg/p1030681.htm "Enigma M4 message p1030681, Crypto museum").

### Decoding the ciphertext

The full text of the transmission is as follows:

```
DUHF TETO LANO TCTO UARB BFPM HPHG CZXT DYGA HGUF XGEW KBLK GJWL QXXT
GPJJ AVTO CKZF SLPP QIHZ FXOE BWII EKFZ LCLO AQJU LJOY HSSM BBGW HZAN
VOII PYRB RTDJ QDJJ OQKC XWDN BBTY VXLY TAPG VEAT XSON PNYN QFUD BBHH
VWEP YEYD OHNL XKZD NWRH DUWU JUMW WVII WZXI VIUQ DRHY MNCY EFUA PNHO
TKHK GDNP SAKN UAGH JZSM JBMH VTRE QEDG XHLZ WIFU SKDQ VELN MIMI THBH
DBWV HDFY HJOQ IHOR TDJD BWXE MEAY XGYQ XOHF DMYU XXNO JAZR SGHP LWML
RECW WUTL RTTV LBHY OORG LGOW UXNX HMHY FAAC QEKT HSJW DUHF TETO
```

We start with the day's basic settings, printed ahead of time in a book distributed to captains.

* rotors: `BETA`, `V`, `VI`, `VIII`

* reflector: `UKWC`

* ringstellung: `'EPEL'`

* plugboard: `AE BF CM DQ HU JN LX PR SZ VW`

* grundstellung: `'NAEM'`

We create an enigma instance with these settings, including the doublestep bug which the M4 had:

```python
>>> from enigma import *
>>> m4 = Enigma(rotors=(BETA, V, VI, VIII), reflector=UKWC_THIN,
ringstellung='EPEL', doublestep=True, grundstellung='NAEM',
plugboard=['AE', 'BF', 'CM', 'DQ', 'HU', 'JN', 'LX', 'PR', 'SZ', 'VW'])
```

The first and last eight characters of the message tell us what the grundstellung (ground settings) will be to decode the main message. Via a lookup table, we turn `'DUHF TETO'` into `'QEOB'`. We then decode this using the provided grundstellung `'NAEM'`:

```python
>>> m4.encode('QEOB')
'CDSZ'
```

We then use the result `'CDSZ'` as our grundstellung for the actual decryption, leaving off the indicator characters at the start and end:

```python
>>> ciphertext = """LANOTCTOUARBBFPMHPHGCZXTDYGAHGUFXGEWKBLKGJWLQXXTGPJJAVTOCKZFSLPPQIHZFXOEBWIIEKFZLCLOAQJULJOYHSSMBBGWHZANVOIIPYRBRTDJQDJJOQKCXWDNBBTYVXLYTAPGVEATXSONPNYNQFUDBBHHVWEPYEYDOHNLXKZDNWRHDUWUJUMWWVIIWZXIVIUQDRHYMNCYEFUAPNHOTKHKGDNPSAKNUAGHJZSMJBMHVTREQEDGXHLZWIFUSKDQVELNMIMITHBHDBWVHDFYHJOQIHORTDJDBWXEMEAYXGYQXOHFDMYUXXNOJAZRSGHPLWMLRECWWUTLRTTVLBHYOORGLGOWUXNXHMHYFAACQEKTHSJW"""
>>> plaintext = m4.encode(ciphertext, 'CDSZ')
>>> plaintext
'KRKRALLEXXFOLGENDESISTSOFORTBEKANNTZUGEBENXXICHHABEFOLGELNBEBEFEHLERHALTENXXJANSTERLEDESBISHERIGXNREICHSMARSCHALLSJGOERINGJSETZTDERFUEHRERSIEYHVRRGRZSSADMIRALYALSSEINENNACHFOLGEREINXSCHRIFTLSCHEVOLLMACHTUNTERWEGSXABSOFORTSOLLENSIESAEMTLICHEMASSNAHMENVERFUEGENYDIESICHAUSDERGEGENWAERTIGENLAGEERGEBENXGEZXREICHSLEITEIKKTULPEKKJBORMANNJXXOBXDXMMMDURNHFKSTXKOMXADMXUUUBOOIEXKP'
```

This is the full message, which we can now see contains some spelling errors (for instance, `'HVRRGRZSSADMIRAL'` should be `'HERRGROSSADMIRAL'`).

### Formatting the plaintext

We can make this somewhat more legible by replacing the letters often used as punctuation:

```python
>>> punctuation =  (('XX', ':\n'), ('Y', ', '), ('X', '. '))
>>> punctedtext = plaintext
>>> for c, p in punctuation:
...     punctedtext = punctedtext.replace(c, p)
... 
>>> import re
>>> # J was used as an apostrophe, and never occurs between two consonants in German
>>> punctedtext = re.sub('(?<=[^AEIOU])J(?=[^AEIOU])', "'", punctedtext)
```

The pair `'KK'` is used for brackets, so we replace them based on parity (assuming for simplicity's sake that the message doesn't have nested brackets):

```python
>>> bracketsearcher = (i for i in range(len(punctedtext)) if punctedtext.startswith('KK', i))
>>> for num, pos in enumerate(bracketsearcher):
...     if num % 2:
...         bracket = ') '
...     else:
...         bracket = ' ('
...     punctedtext = punctedtext[: pos] + bracket + punctedtext[pos+2:]
... 
>>> 
```

We end up with the text below. Still not super readable, but if you know German it's not too difficult. However, there's still plenty of standard abbreviations and spelling mistakes. In particular, "Bisherigen" was misspelt as "BISHERIGXN", and the X was turned into a full stop by our formatting, leaving "BISHERIG. N". Even without the spelling mistakes ("DURNH" should be "DURCH", "BOOIE" should be "BOOTE"), the final line is unintelligible to a normal German speaker.

>KRKRALLE:
>FOLGENDESISTSOFORTBEKANNTZUGEBEN:
>ICHHABEFOLGELNBEBEFEHLERHALTEN:
>JANSTERLEDESBISHERIG. NREICHSMARSCHALLS'GOERING'SETZTDERFUEHRERSIE, HVRRGRZSSADMIRAL, ALSSEINENNACHFOLGEREIN. SCHRIFTLSCHEVOLLMACHTUNTERWEGS. ABSOFORTSOLLENSIESAEMTLICHEMASSNAHMENVERFUEGEN, DIESICHAUSDERGEGENWAERTIGENLAGEERGEBEN. GEZ. REICHSLEITEI (TULPE) 'BORMANN':
>OB. D. MMMDURNHFKST. KOM. ADM. UUUBOOIE. KP

The translated message reads:

>WAR EMERGENCY MESSAGE [To] All:
   
>The following is to be announced immediately: I have received the following order: 'In place of former Reichsmarschall 'Göring', the Führer has appointed you, Herr Grossadmiral, as his successor. Written authorization [is] on the way. Effective immediately, you are to order all measures that are required by the present situation.

>Signed, Reichsleiter (Tulpe) 'Bormann': [From] Commander-in-Chief of the Navy, [sent] by way of the Radio Station of the Commanding Admiral of Submarines

# Classes

The class inheritance diagram is:

```
            Rotor
           /     \
          /       \
_InternalRotor   Reflector
          \       /
           \     /
     _InternalReflector
```

## enigma.Rotor(object)

One of the wheels (Walze) that permute the characters in the encoding.

### attributes

Rotor.**wiring: `str`**. The fixed permutation of the alphabet

Rotor.**notch: `Optional[str]`**. When the rotor turns past a notch value, it turns the rotor to the left of it.

Rotor.**ring: `str`**. An adjustable ring that offsets the rotor's mapping. For instance, if the ring is `'C'` 

```python
I = Rotor(wiring='EKMFLGDQVZNTOWYHXUSPAIBRCJ', notch='Q')
II = Rotor('AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E')
III = Rotor('BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V') 
IV = Rotor('ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J')
V = Rotor('VZBRGITYUPSDNHLXAWMJQOFECK', 'Z')
VI = Rotor('JPGVOUMFYQBENHZRDKASXLICTW', 'ZM')
VII = Rotor('NZJHGRCXMYSWBOUFAIVLPEKQDT', 'ZM')
VIII = Rotor('FKQHTLXOCBJSPDZRAMEWNIUYGV', 'ZM')
BETA = Rotor('LEYJVCNIXWPBQMDRTAKZGFUHOS')
GAMMA = Rotor('FSOKANUERHMBTIYCWLQPZXVGJD')
```

## enigma.Reflector(Rotor)

A subclass of Rotor which has a self-inverse mapping, i.e. where if `c1` maps to `c2`, then `c2` maps to `c1`. Here, "`c1` maps to `c2`" means that `wiring.index(c1) == c2`.

The constructor takes only the argument `wiring: str`.

The predefined reflectors are:
```python
UKWB = Reflector(wiring='YRUHQSLDPXNGOKMIEBFZCWVJAT')
UKWC = Reflector('FVPJIAOYEDRZXWGCTKUQSBNMHL')
UKWB_THIN = Reflector('ENKQAUYWJICOPBLMDXZVFTHRGS')
UKWC_THIN = Reflector('RDOBJNTKVEHMLFCWZAXGYIPSUQ')
```

'UKW' stands for 'Umkehrwalze', meaning 'reflector rotor' in German.

## enigma._InternalRotor(Rotor)

A rotor within the context of an Enigma instance. This has a defined position, and can therefore translate letters backwards and forwards, as well as turn.

The constructor takes the arguments `baserotor: Rotor` and `pos: str`.

### attributes

Inherits attributes from `Rotor`, and also:

_InternalRotor.**baserotor: `Rotor`**. The instance of `Rotor` whose attribute values are inherited.

_InternalRotor.**pos: `int`**. An int from 0 to 25 which tracks the wheel's rotation.

_InternalRotor.**mapping: `str`**. The rotor's permutation of the alphabet using `self.wiring`, `self.pos` and `self.ring`.

### methods

_InternalRotor.**remap()**. Recalculate `self.mapping` using `self.wiring`, `self.pos` and `self.ring`.

_InternalRotor.**right2left(char: str) -> str**. Encode from right to left (before reflector) relative to `'A'`.

_InternalRotor.**left2right(char: str) -> str**. Encode from left to right (after reflector) relative to `'A'`.

_InternalRotor.**turn()**. Increment `self.pos` by 1 (mod 26) and adjusts mapping accordingly.

## class enigma._InternalReflector(Reflector, _InternalRotor)

Its constructor takes only the argument `basereflector: Reflector`.

### methods

_InternalReflector.**reflect(char: str) -> str**. Encodes `char` in a self-inverse way. An analogue for `_InternalRotor.right2left` and `_InternalRotor.left2right`, except it doesn't require the rotor to have a defined position.

## class enigma.Enigma

The "properties" sub-section is a list of the arguments that can be given to the constructor (without the "`Enigma.`" in front of them).

### properties

Each of the following attributes is a property with a setter, meaning it is accessed like a normal attribute and set in the way that you would set a normal variable (see the examples above). See the "Basic controls" subsection for more details.

Enigma.**rotors: `tuple[Rotor, ...]`**. Can take 3 or 4 rotors. Valid elements of the tuple argument rotors are given in `ROTORLIST`. If 4 rotors are given, then the 4th (leftmost) rotor must be a "Greek wheel" (`BETA` or `GAMMA`), and the reflector must be `UKWB_THIN` or `UKWC_THIN`. The Greek wheels can't be used in any position other than the 4th.

Enigma.**reflector: `Reflector`**. Valid values for reflector are given in `REFLECTORLIST`. If 3 rotors are used then the reflector must be `UKWB` or `UKWC`, if 4 rotors are used it must be `UKWB_THIN` or `UKWC_THIN`.

Enigma.**ringstellung: `str`**. The option `ringstellung` is an offset applied to each rotor which changes its mapping. As such it must be a list of letters with the same length as the number of rotors. For instance, a machine with rotor configuration `(I, II, III)` given ringstellung `'ABC'` will give `I` ring `'A'`, `II` ring `'B'`, `III` ring `'C'`.

Enigma.**plugboard: `Iterable[str]`**. The plugboard connects pairs of letters, swapping them before and after the signal has been through the rotors. The argument plugboard must be an iterable of pairs of letters with no letter used twice, so `['AB', 'CD']` is a valid pluglist while `['AB', 'BC']` and `['ABC']` aren't.

Enigma.**doublestep: `bool`**. If `doublestep == True`, replicates a bug in some enigma machines which caused the middle rotor to turn more frequently. See https://en.wikipedia.org/wiki/Enigma_rotor_details#Normalized_Enigma_sequences for more details. This bug was present in the M3 and M4 machines, which are the primary versions intended to be modelled by this module.
 
Enigma.**grundstellung: `str`**. The starting positions of each rotor, given as a string of characters. A machine with rotor configuration `(I, II, III)` given grundstellung `'ABC'` will have `I` start at position `'A'`, `II` at `'B'`, and `III` at `'C'`.

### methods

Enigma.**encode(message: str, grundstellung: Optional[str] = None) -> str**. Encodes the message using the provided `grundstellung`. If `grundstellung` is `None`, use the final positions from the previous use.

### attributes

The inner workings of the Enigma class, these should normally only be accessed via the corresponding properties above.

Enigma.**_rotors: `tuple[_InternalRotor]`**.

Enigma.**_reflector: `_InternalReflector`**.

Enigma.**_plugboard: `dict`**. This is a dict where each key is also a value of the dict, and each value is also a key. More explicitly, if `e` is an instance of `Enigma`, then `e._plugboard[e._plugboard[k]] == k` for each `k` in `e._plugboard.keys()`. For example, `e.plugboard = ['AB', 'CD']` sets `e._plugboard` to `{'A': 'B', 'C': 'D', 'B': 'A', 'D': 'C'}`.

Each setting in the ringstellung is held in its associated `_InternalRotor` (see `Rotor.ring`).

Each setting of the grundstellung is held in the associated `_InternalRotor` (see `_InternalRotor.pos`).
