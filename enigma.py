"""Mimics an enigma machine, specifically the Kriegsmarine M3/M4.

https://www.cryptomuseum.com/crypto/enigma/m3/index.htm

To do:
* add a 'verbose' option to Enigma.encode() which shows the state for each step
(like https://en.wikipedia.org/wiki/Enigma_machine#Example_enciphering_process)
"""

from typing import Iterable, Optional

ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class RotorError(Exception):
    pass

class Rotor(object):
    """One of the wheels (Walze) that permute the characters in the encoding.
    
    The list of pre-defined Rotors is ROTORLIST."""

    def __init__(self, wiring: str, notch: Optional[str] = None, ring: str = 'A'):
        if len(wiring) != 26 or not wiring.isalpha() or len(set(wiring)) < 26:
            raise RotorError("Invalid argument 'wiring'. Must be a permutation of the alphabet.")
        else:
            self.wiring = wiring.upper()
        if len(ring) != 1 or not ring.isalpha():
            raise ValueError("ring must be a single letter.")
        else:
            self.ring = ABC.index(ring.upper())
        # not all rotors turn, so they don't all need notch values
        if notch is None:
            self.notch = None
        elif len(notch) not in {1, 2}:
            raise ValueError('Rotor must have one or two notches.')
        else:
            self.notch = {ABC.index(c) for c in notch}

    def __repr__(self) -> str:
        try:
            notches = "'" + "".join([ABC[n] for n in self.notch]) + "'"
        except TypeError:
            notches = None
        settings = ", ".join([f"wiring='{self.wiring}'", f"notch={notches}", 
        f"ring='{ABC[self.ring]}'"])
        return f"Rotor({settings})"


class _InternalRotor(Rotor):
    """A rotor within the context of an Enigma instance. 
    
    This has a defined position, and can therefore translate letters
    backwards and forwards, as well as turn."""

    def __init__(self, baserotor: Rotor, pos: str = 'A'):
        if baserotor.notch is None:
            # rotors can have no notches (e.g. BETA) or more than one (e.g. VI)
            notches = None
        else:
            notches =  ''.join([ABC[n] for n in baserotor.notch])
        super().__init__(baserotor.wiring, notches, ABC[baserotor.ring])
        self.baserotor = baserotor
        if len(pos) == 1 and pos.isalpha():
            self.pos = ABC.index(pos.upper())
        else:
            raise RotorError("'pos' must be a letter.")
        self.remap()

    def __repr__(self) -> str:
        rotorname = ROTORLIST.get(self.baserotor, self.baserotor)
        return f"_InternalRotor(baserotor={rotorname}, pos='{ABC[self.pos]}')"

    def remap(self):
        """Recalculate self.mapping using self.wiring, self.pos and self.ring."""
        w = ''.join([ABC[(ABC.index(char)+self.ring) % 26] for char in self.wiring])
        self.mapping = w[(self.pos-self.ring) % 26: ] + w[: (self.pos-self.ring) % 26]

    def right2left(self, char: str) -> str:
        """Encode from right to left (before reflector) relative to 'A'."""
        newchar = self.mapping[ABC.index(char) % 26]
        return ABC[(ABC.index(newchar) - self.pos) % 26]
    
    def left2right(self, char: str) -> str:
        """Encode from left to right (after reflector) relative to 'A'."""
        newchar = ABC[(ABC.index(char) + self.pos) % 26]
        return ABC[self.mapping.index(newchar) % 26]

    def turn(self):
        """Increment self.pos by 1 (mod 26) and adjust mapping accordingly."""
        self.pos  = (self.pos + 1) % 26
        self.mapping = self.mapping[1: ] + self.mapping[0]


class Reflector(Rotor):
    """A subclass of Rotor which has a self-inverse mapping.

    In other words, if c1 maps to c2, then c2 maps to c1 (In this case, 
    "maps to" means that wiring.index(c1) == c2)."""

    def __init__(self, wiring: str):
        Rotor.__init__(self, wiring)
        w = wiring.upper()
        for i, c in enumerate(ABC):
            if w[i] != ABC[w.index(c)]:
                raise RotorError('Reflector must be its own inverse.')

    def __repr__(self) -> str:
        return f"Reflector(wiring='{self.wiring}')"


class _InternalReflector(Reflector, _InternalRotor):

    def __init__(self, basereflector: Reflector):
        super().__init__(basereflector.wiring)
        self.baserotor = basereflector

    def reflect(self, char: str) -> str:
        """Encode a character in a self-inverse way. 
        
        Similar to _InternalRotor.right2left, except it doesn't require 
        the rotor to have a defined position."""
        return self.wiring[ABC.index(char.upper())]


I = Rotor(wiring='EKMFLGDQVZNTOWYHXUSPAIBRCJ', notch='Q')
II = Rotor('AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E')
III = Rotor('BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V') 
IV = Rotor('ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J')
V = Rotor('VZBRGITYUPSDNHLXAWMJQOFECK', 'Z')
VI = Rotor('JPGVOUMFYQBENHZRDKASXLICTW', 'ZM')
VII = Rotor('NZJHGRCXMYSWBOUFAIVLPEKQDT', 'ZM')
VIII = Rotor('FKQHTLXOCBJSPDZRAMEWNIUYGV', 'ZM')

# the following rotors do not turn, so they don't need notches
# BETA and GAMMA should only be used in the rightmost position of m4
BETA = Rotor('LEYJVCNIXWPBQMDRTAKZGFUHOS')
GAMMA = Rotor('FSOKANUERHMBTIYCWLQPZXVGJD')

UKWB = Reflector('YRUHQSLDPXNGOKMIEBFZCWVJAT')
UKWC = Reflector('FVPJIAOYEDRZXWGCTKUQSBNMHL')
# for use with BETA and GAMMA only
UKWB_THIN = Reflector('ENKQAUYWJICOPBLMDXZVFTHRGS')
UKWC_THIN = Reflector('RDOBJNTKVEHMLFCWZAXGYIPSUQ')

ROTORLIST = {
    I: 'I', II: 'II', III: 'III', IV: 'IV', V: 'V', VI: 'VI',
    VII: 'VII', VIII: 'VIII', BETA: 'BETA', GAMMA: 'GAMMA'
    }

REFLECTORLIST = {
    UKWB: 'UKWB', UKWC: 'UKWC', 
    UKWB_THIN: 'UKWB_THIN', UKWC_THIN: 'UKWC_THIN'
    }

class EnigmaError(Exception):
    pass

class Enigma(object):
    """The actual machine. 
    
    Can take 3 or 4 rotors. Valid elements of the tuple argument rotors are
    given in ROTORLIST. If 4 rotors are given, then the 4th (leftmost) rotor
    must be either BETA or GAMMA, and the reflector must be UKWB_THIN or 
    UKWC_THIN. BETA, GAMMA, UKWB_THIN and UKWC_THIN cannot be used in a 
    3-rotor instance.

    Valid values for reflector are given in REFLECTORLIST. If 3 rotors are
    used then the reflector cannot be UKWB_THIN or UKWC_THIN, if 4 rotors
    are used it cannot be UKWB or UKWC.
    
    ringstellung is an offset applied to each rotor which changes its mapping.
    As such it must be a list of letters with the same length as the number
    of rotors. For instance, a machine with rotor configuration (I, II, III)
    given ringstellung 'ABC' will give I ring 'A', II ring 'B', III ring 'C'.
    
    The plugboard connects pairs of letters, swapping them before and also
    after the signal has been through the rotors. The argument plugboard must
    be an iterable of pairs of letters with no letter used twice, so 
    ['AB', 'CD'] is a valid pluglist while ['AB', 'BC'] and ['ABC'] aren't.
    
    If doublestep == True, replicates a bug in some enigma machines which caused
    the middle rotor to turn more frequently."""

    def __init__(self, rotors: tuple[Rotor, ...], reflector: Reflector, ringstellung: str = '',
    plugboard: Iterable[str] = [], doublestep: bool = True, grundstellung: str = ''):
        self.reflector = reflector
        self.rotors = rotors
        if not ringstellung:
            ringstellung = 'A'*len(rotors)
        self.ringstellung = ringstellung
        if not grundstellung:
            grundstellung = 'A'*len(rotors)
        self.grundstellung = grundstellung
        self.plugboard = plugboard
        if isinstance(doublestep, bool):
            self.doublestep = doublestep
        else:
            raise TypeError("argument 'doublestep' must have type 'bool'")


    def __repr__(self) -> str:
        settings = ', '.join([f"rotors={self.rotors}", f"reflector={self.reflector}",
            f"ringstellung='{self.ringstellung}'", f"grundstellung='{self.grundstellung}'", 
            f"plugboard={self.plugboard}", f"doublestep={self.doublestep}"]
            )
        return f'Enigma({settings})'

    @property
    def grundstellung(self):
        """The position of each rotor, as a list of letters.
        
        Internally, these are attributes _InternalRotor.pos, an int from
        0 to 25 for each rotor, but they are displayed as a string of
        letters like they are in a real enigma machine."""
        return ''.join([ABC[r.pos] for r in self._rotors])

    @grundstellung.setter
    def grundstellung(self, grundstellung: str):
        if not isinstance(grundstellung, str):
            raise TypeError('Grundstellung must be a string.')
        if not grundstellung.isalpha():
            raise ValueError('Grundstellung must consist only of letters.')
        if len(grundstellung) != len(self._rotors):
            raise EnigmaError('Grundstellung does not match number of rotors.')
        for rotor, pos in zip(self._rotors, grundstellung.upper()):
            rotor.pos = ABC.index(pos)
            rotor.remap()

    @property
    def ringstellung(self):
        """An offset applied to each rotor which changes its mapping.
        
        Internally, these are attributes _InternalRotor.ring, an int from
        0 to 25 for each rotor, but they are displayed as a string of
        letters like they are in a real enigma machine."""
        return ''.join([ABC[r.ring] for r in self._rotors])

    @ringstellung.setter
    def ringstellung(self, ringstellung: str = 'AAA'):
        if len(self._rotors) != len(ringstellung):
            raise EnigmaError('Ringstellung does not match number of rotors.')
        if not ringstellung.isalpha():
            raise ValueError('Ringstellung must be a string of letters.')
        for r, ring in zip(self._rotors, ringstellung.upper()):
            r.ring = ABC.index(ring)
            r.remap()
    
    @property
    def plugboard(self):
        """A self-inverse mapping applied before and after the rotors.
            
        plugboard must be an iterable of pairs of letters, with no letter 
        appearing more than once in the iterable. The list ['AB', 'CD'] is a
        valid assignment, ['ABD'] and ['AB', 'BC'] are not.
        Internally, e._plugboard is a dict with 
        e._plugboard[e._plugboard[k]] == k for each k in e._plugboard.keys().

        Example: e.plugboard = ['AB', 'CD'] sets e._plugboard to 
        {'A': 'B', 'C': 'D', 'B': 'A', 'D': 'C'}."""
        return [key + val for (key, val) in self._plugboard.items() if key < val]

    @plugboard.setter
    def plugboard(self, plugboard: Iterable[str]):
        if not plugboard:
            # have to check this case separately otherwise the join check fails
            self._plugboard = {}
            return
        plugstr = ''.join(plugboard)
        if any(len(p) != 2 for p in plugboard) or not plugstr.isalpha():
            raise ValueError('plugboard must consist of pairs of letters.')
        if any(plugstr.count(c) > 1 for c in plugstr):
            # test for repeated letters
            raise ValueError('plugboard must contain each letter at most once.')
        self._plugboard = {}
        for pair in plugboard:
            if pair[0] == pair[1]:
                # ignore letters mapped to themselves
                continue
            pair = pair.upper()
            self._plugboard[pair[0]] = pair[1]
            self._plugboard[pair[1]] = pair[0]

    @property
    def reflector(self):
        return REFLECTORLIST.get(self._reflector.baserotor, self._reflector)

    @reflector.setter
    def reflector(self, reflector: Reflector):
        self._reflector = _InternalReflector(reflector)

    @property
    def rotors(self):
        rotorlist = [ROTORLIST.get(r.baserotor, r) for r in self._rotors]
        return str(tuple(rotorlist)).replace("'", "")

    @rotors.setter
    def rotors(self, rotors: tuple[Rotor, ...] = ()):
        if len(rotors) == 3:
            if BETA in rotors or GAMMA in rotors:
                raise EnigmaError("BETA and GAMMA can't be used in a three-rotor enigma.")
            if self._reflector.baserotor in {UKWB_THIN, UKWC_THIN}:
                raise EnigmaError("Thin reflector can't be used in a three-rotor enigma.")
        elif len(rotors) == 4:
            if rotors[0] not in {BETA, GAMMA}:
                raise EnigmaError("Fourth rotor must be BETA or GAMMA.")
            if self._reflector.baserotor in {UKWB, UKWC}:
                raise EnigmaError("Thin reflector must be used in four-rotor enigma.")
        else:
            raise EnigmaError('Please select 3 or 4 rotors.')
        self._rotors = tuple(_InternalRotor(r, 'A') for r in rotors)


    def encode(self, message: str, grundstellung: Optional[str] = None) -> str:
        """Turns plaintext to ciphertext and ciphertext into plaintext.
        
        grundstellung is the inital settings for the rotors, expressed
        as letters, one for each rotor. For instance, a machine with rotor
        configuration (I, II, III) given grundstellung 'ABC' will have
        I start at 'A', II at 'B', III at 'C'. If grundstellung is not 
        provided then it uses the final settings from the last use.
        
        Example:
        >>> e = Enigma(rotors=(I, II, III), reflector=UKWB, ringstellung='AAA',
        plugboard=[], doublestep=True)
        >>> e.encode('AAAAA', 'AAA')
        'BDZGO'
        >>> m4 = Enigma(rotors=(BETA, V, VI, VIII), reflector=UKWC_THIN,
        ringstellung='EPEL', doublestep=True, grundstellung='NAEM'
        plugboard=['AE', 'BF', 'CM', 'DQ', 'HU', 'JN', 'LX', 'PR', 'SZ', 'VW'])
        >>> m4.encode('QEOB') # uses grundstellung 'NAEM'
        'CDSZ'
        ."""

        if not message.isalpha():
            raise EnigmaError('Message must consist only of letters.')
        if grundstellung:
            self.grundstellung = grundstellung
        ciphertext = ''
        for char in message.upper():
            # wheels are turned before the electrical connections are made
            if self.doublestep and self._rotors[-2].pos in self._rotors[-2].notch:
                self._rotors[-2].turn()
                self._rotors[-3].turn()
            elif self._rotors[-1].pos in self._rotors[-1].notch:
                if self._rotors[-2].pos in self._rotors[-2].notch:
                    self._rotors[-3].turn()
                self._rotors[-2].turn()
            self._rotors[-1].turn()
            # signal goes through the plugboard, through the rotors, across the reflector, 
            # back through the rotors and then back through the plugboard. Diagram:
            # https://commons.wikimedia.org/wiki/File:Enigma_wiring_kleur.svg
            newchar = self._plugboard.get(char, char)
            # reversed because connection goes from right to left first
            for rotor in reversed(self._rotors):
                newchar = rotor.right2left(newchar)
            newchar = self._reflector.reflect(newchar)
            for rotor in self._rotors:
                newchar = rotor.left2right(newchar)
            newchar = self._plugboard.get(newchar, newchar)
            ciphertext += newchar
        return ciphertext
