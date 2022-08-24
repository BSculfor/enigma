from enigma import *
from enigma import _InternalRotor, _InternalReflector
import unittest as ut

e = Enigma(rotors=(I, II, III), reflector=UKWB,
           ringstellung='AAA', doublestep=False)
m4 = Enigma((BETA, V, VI, VIII), reflector=UKWC_THIN,
            plugboard=['AE', 'BF', 'CM', 'DQ', 'HU', 'JN', 'LX', 'PR', 'SZ', 'VW'],
            ringstellung='EPEL', doublestep=True)

ROTORLIST = [I, II, III, IV, V, VI, VII, VIII, BETA, GAMMA]
REFLECTORLIST = [UKWB, UKWC, UKWB_THIN, UKWC_THIN]

class TestRotors(ut.TestCase):

    def test_repr(self):
        e = Enigma(rotors=(I, II, III), reflector=UKWB,
           ringstellung='AAA', doublestep=False)
        I.__repr__()
        UKWB.__repr__()
        e.rotors[0].__repr__()
        e.reflector.__repr__()
    
    def test_symmetry(self):
        for r in ROTORLIST:
            r1 = _InternalRotor(r, pos='A')
            for c in ABC:
                self.assertEqual(r1.right2left(r1.left2right(c)), c)
                self.assertEqual(r1.left2right(r1.right2left(c)), c)

    def test_reflection(self):
        for r in REFLECTORLIST:
            r1 = _InternalReflector(r)
            for c in ABC:
                self.assertEqual(r1.reflect(r1.reflect(c)), c)
                self.assertEqual(r1.reflect(r1.reflect(c)), c)

    def test_turn(self):
        for _ in range(26):
            # BETA and GAMMA never turn so don't need to test them
            # neither do reflectors
            for r in ROTORLIST[: -2]:
                r1 = _InternalRotor(r, pos='A')
                oldmap, oldpos = r1.mapping, r1.pos
                r1.turn()
                self.assertEqual(r1.mapping, oldmap[1: ] + oldmap[0])
                self.assertEqual(r1.pos, (oldpos + 1) % 26)

    def test_init(self):
        with self.assertRaises(RotorError):
            # left2right(right2left('a')) != 'a'
            _ = Reflector('zacdefghijklmnopqrstuvwxyb')
        with self.assertRaises(RotorError):
            # has 'a' twice
            _ = Rotor('zacdefghijklmnopqrstuvwxya')
                

class TestEnigma(ut.TestCase):

    def test_repr(self):
        e = Enigma(rotors=(I, III, V), reflector=UKWB,
           ringstellung='AAA', doublestep=False)
        self.assertEqual(e.__repr__(), "Enigma(rotors=(I, III, V), reflector=UKWB, ringstellung='AAA', grundstellung='AAA', plugboard=[], doublestep=False)")

    def test_plugboard(self):
        # check valid assignments
        e.plugboard = ['AB']
        e.plugboard = ['cd']
        e.plugboard = []
        e.plugboard = ['AB', 'CD', 'EF']
        # check that the mapping is self-inverse
        assert all(e._plugboard[e._plugboard[k]] == k for k in e._plugboard.keys())
        # check the getter
        self.assertEqual(e.plugboard, ['AB', 'CD', 'EF'])
        with self.assertRaises(ValueError):
            # check non-pairs don't work
            e.plugboard = ['ABC']
        with self.assertRaises(ValueError):
            # check impossible wirings don't work
            e.plugboard = ['AB', 'BC']
        with self.assertRaises(ValueError):
            # check invalid characters don't work
            e.plugboard = ['A1']

    def test_ringstellung(self):
        e.ringstellung = 'FCD'
        self.assertEqual([r.ring for r in e._rotors], [5, 2, 3])
        with self.assertRaises(EnigmaError):
            # check incorrect argument length doesn't work
            e.ringstellung = 'A'
        with self.assertRaises(ValueError):
            # check impossible values don't work
            e.ringstellung = 'A1A'

    def test_grundstellung(self):
        e.grundstellung = 'AAA'
        m4.grundstellung = 'AAAA'
        with self.assertRaises(ValueError):
            # check impossible values don't work
            e.grundstellung = 'A1A'
        with self.assertRaises(EnigmaError):
            # check incorrect argument length doesn't work
            e.grundstellung = 'AAAA'

    def test_rotors(self):
        e.rotors = (I, III, V)
        with self.assertRaises(EnigmaError):
            e.rotors = (BETA, I, II)
        with self.assertRaises(EnigmaError):
            e.rotors = (V, III, I, II)
        with self.assertRaises(EnigmaError):
            m4.rotors = (BETA, I, II)

    # https://en.wikipedia.org/wiki/Enigma_rotor_details#Normalized_Enigma_sequences
    def test_doublestep(self):
        edoublestep = Enigma(rotors=(I, II, III), reflector=UKWB,
                             ringstellung='AAA', doublestep=True)
        # check that a normal sequence works fine
        edoublestep.encode('HELLO', 'AAT')
        self.assertEqual(edoublestep.grundstellung, 'ABY')
        # check that the double-step actually happens
        edoublestep.encode('HELLO', 'ADT')
        self.assertEqual(edoublestep.grundstellung, 'BFY')
        edoublestep.doublestep = False
        # check that doublestep doesn't happen if doublestep == False
        edoublestep.encode('HELLO', 'ADT')
        self.assertEqual(edoublestep.grundstellung, 'AEY')

    def test_M3_encode_norings(self):
        e = Enigma(rotors=(I, II, III), reflector=UKWB,
           ringstellung='AAA')
        self.assertEqual(e.encode('AAAAA', 'AAA'), 'BDZGO')

    def test_M3_encode_rings(self):
        e = Enigma(rotors=(I, II, III), reflector=UKWB,
           ringstellung='BBB')
        self.assertEqual(e.encode('AAAAA', 'AAA'), 'EWTYX')
        # check that it decodes properly as well
        self.assertEqual(e.encode('EWTYX', 'AAA'), 'AAAAA')

    def test_M4_encode(self):
        m4 = Enigma((BETA, V, VI, VIII), reflector=UKWC_THIN, ringstellung='EPEL',
                    plugboard=['AE', 'BF', 'CM', 'DQ', 'HU', 'JN', 'LX', 'PR', 'SZ', 'VW'],
                    doublestep=True)
        self.assertEqual(m4.encode('QEOB', 'NAEM'), 'CDSZ')
        # the start of the 'Dönitz message' which announced Dönitz had become Fuhrer
        self.assertEqual(
            m4.encode('LANOTCTOUARBBFPMHPHGCZXTDYGAHGUFXGEWKBLKGJWL', 'CDSZ'),
                      'KRKRALLEXXFOLGENDESISTSOFORTBEKANNTZUGEBENXX'
            )
        self.assertEqual(
            m4.encode('KRKRALLEXXFOLGENDESISTSOFORTBEKANNTZUGEBENXX', 'CDSZ'),
                      'LANOTCTOUARBBFPMHPHGCZXTDYGAHGUFXGEWKBLKGJWL'
            )


if __name__ == '__main__':
    ut.main()
