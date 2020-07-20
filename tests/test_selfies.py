import faulthandler
import random

import pytest
from rdkit.Chem import MolFromSmiles

import selfies as sf

faulthandler.enable()


@pytest.fixture()
def max_len():
    return 200


@pytest.fixture()
def hard_alphabet():
    """A challenging alphabet of SELFIES symbols.
    """

    alphabet = sf.get_alphabet()

    # add some challenging symbols
    alphabet.update([
        '[epsilon]', '.', '[/C]', '[\\C]', '[/N]', '[\\N]',
        '[Expl=Ring1]', '[Expl#Ring1]', '[=Br]'
    ])
    return alphabet


def test_random_selfies_decoder(trials, max_len, hard_alphabet):
    """Tests if SELFIES that are generated by randomly stringing together
    symbols from the SELFIES alphabet are decoded into valid SMILES.
    """

    sf.set_alphabet()  # re-set alphabet
    alphabet = tuple(hard_alphabet)

    for _ in range(trials):

        # create random SELFIES and decode
        rand_len = random.randint(1, max_len)
        rand_mol = ''.join(random.choices(alphabet, k=rand_len))
        smiles = sf.decoder(rand_mol)

        # check if SMILES is valid
        try:
            is_valid = MolFromSmiles(smiles, sanitize=True) is not None
        except Exception:
            is_valid = False

        assert is_valid, f"Invalid SMILES {smiles} decoded from {sf}."


def test_nop_symbol_decoder(trials, max_len, hard_alphabet):
    """Tests that the '[nop]' symbol is decoded properly, i.e., it is
    always skipped over.
    """

    sf.set_alphabet()

    alphabet = list(hard_alphabet)
    alphabet.remove('[nop]')

    for _ in range(trials):

        # create random SELFIES with and without [nop]
        rand_len = random.randint(1, max_len)

        rand_mol = random.choices(alphabet, k=rand_len)
        rand_mol.extend(['[nop]'] * rand_len)
        random.shuffle(rand_mol)

        with_nops = ''.join(rand_mol)
        without_nops = with_nops.replace('[nop]', '')

        assert sf.decoder(with_nops) == sf.decoder(without_nops)


def test_get_alphabet_and_atom_dict():
    """Tests selfies.get_alphabet() and selfies.get_atom_dict().
    """

    # Getting the alphabet and atom_dict does not return aliases
    assert sf.get_alphabet() is not sf.get_alphabet()
    assert sf.get_atom_dict() is not sf.get_atom_dict()

    # The appropriate symbols are in the alphabet
    alphabet = sf.get_alphabet()
    assert '[epsilon]' not in alphabet
    assert '.' not in alphabet
    assert '[nop]' in alphabet

    # The appropriate symbols are in atom_dict()
    atom_dict = sf.get_atom_dict()
    assert '?' in atom_dict
