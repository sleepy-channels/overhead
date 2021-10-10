from bitcoinutils.constants import SATOSHIS_PER_BITCOIN
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
from identity import Id
from helper import print_tx, gen_secret
# from typing import List


def main():
    """
    Run main to print the size of the different transactions to the console
    """
    # Some addresses on the testnet
    id_a = Id(
        '6053d21a0a1d0a4c4411b847af085b9441b8605aa97e4ce1c8684e781fb05c20')  # addr: mqNY41TK1fyBobBn4dbDdjfsBHSFZJVuXj
    id_b = Id(
        'e38c1c80e3938fdbcb5538fb19d4968a2758bf2a6310b3da749ef4c7c315b1c4')  # addr: mtuxqJT5rFoBU9kaDxmpsbJkADUuJBMuYG
    id_channel = Id(
        'f8f549c9a4965d0b852d2fdb84dc89c149f9c5b3baf78df4db735de467032982')  # addr: mpdVbUjFsfJB6xjwQbcTFhV76SzW4GrD1H
    id_sleepy_channel_a = Id(
        '1e35ccfc896d2b480e27f56d165d714f947d1a0341f347898585311f2cea3c7b')  # addr: msfj3PQ4TCGCwcUYm8JD2ZDQuvenpx1y3L
    id_exit_a = Id(
        '113f0f1b4371fa20d9df50c9bf4f7013ce1bd36d2050a3d8d1edec9957ca98eb')  # addr: miLumXzHjE5Mr9LQp2Xy3ucVv1gzWo7krb
    id_aux_a = Id(
        '31581750068b41ed6dc6e5d51b0a27de276c990817660ff1ce792e6f32d92e64')  # addr: mg3ZZVgLHk9LFuQJq9MXhfiq4hePJN86BS
    id_sleepy_channel_b = Id(
        'eff4fee98d4bca17b8d3fb24487774b7e1839f6380604cb7eb10b188b5ad1869')  # addr: mzM97A3EeuT66L5UQcs35E9cnFYJ9DQGpd
    id_exit_b = Id(
        'c2679a343f21343e460076ce5d370d33239d7be1c30e756884502c07735e39c7')  # addr: mugN1P3qwe48zwXAGLyKNxuxneiiDMaYPJ
    id_aux_b = Id(
        '81146adeea0bad08271804a51362dceecff546708fc9c29a25ad8f85c2ddb741')  # addr: mxFif3MUvAxwG95GK3PVh6jrdfgJFdGRC1

    tx_input_a = TxInput('486f8bc6f3b73ce20b62d08d88d1331cf3af431031a4e2a4c5c5f732e073a690', 1)
    tx_input_b = TxInput('3447b891d798e8796a1812a26b947d2aeea94b228fa8b8236437bddc957a651d', 1)

    # SATOSHIS_PER_BITCOIN
    fee = 500
    eps = 1
    money_a = int(0.001 * SATOSHIS_PER_BITCOIN)
    money_b = int(0.001 * SATOSHIS_PER_BITCOIN)
    c = int((money_a + money_b)/3)
    v_a = int(c*0.4)
    v_b = c - v_a
    t = '20052F' # hex of block 2098474

    ft = get_ft(tx_input_a, tx_input_b, id_a, id_b, id_channel, v_a+v_b, c, fee)
    print_tx(ft, 'Funding tx')
    state_a = get_state(TxInput(ft.get_hash(), 0), id_channel, id_a, id_sleepy_channel_a, id_exit_a, v_a, v_b, c, fee)
    print_tx(state_a, 'State tx of A')
    slowpay_a = get_slowpay(TxInput(state_a.get_hash(), 1), id_sleepy_channel_a, id_a, v_a, t, fee)
    print_tx(slowpay_a, 'Slow pay tx of A')
    punish_a = get_punish(TxInput(state_a.get_hash(), 1), id_sleepy_channel_a, id_b, v_a, fee)
    print_tx(punish_a, 'Punish tx of B on A')
    fpay1_a = get_fpay1(TxInput(state_a.get_hash(), 2), id_exit_a, id_aux_a, id_b, v_b, c, eps, fee)
    print_tx(fpay1_a, 'Fastpay 1 tx for State A')
    fpay2_a = get_fpay2(TxInput(state_a.get_hash(), 1), TxInput(fpay1_a.get_hash(), 0), id_sleepy_channel_a, id_aux_a, id_a, v_a, eps, fee)
    print_tx(fpay2_a, 'Fastpay 2 tx for State A')
    #####
    state_b = get_state(TxInput(ft.get_hash(), 0), id_channel, id_b, id_sleepy_channel_b, id_exit_b, v_b, v_a, c, fee)
    print_tx(state_b, 'State tx of B')
    slowpay_b = get_slowpay(TxInput(state_b.get_hash(), 1), id_sleepy_channel_b, id_b, v_b, t, fee)
    print_tx(slowpay_b, 'Slow pay tx of B')
    punish_b = get_punish(TxInput(state_b.get_hash(), 1), id_sleepy_channel_b, id_a, v_b, fee)
    print_tx(punish_b, 'Punish tx of A on B')
    fpay1_b = get_fpay1(TxInput(state_b.get_hash(), 2), id_exit_b, id_aux_b, id_a, v_a, c, eps, fee)
    print_tx(fpay1_b, 'Fastpay 1 tx for State B')
    fpay2_b = get_fpay2(TxInput(state_b.get_hash(), 1), TxInput(fpay1_b.get_hash(), 0), id_sleepy_channel_b, id_aux_b, id_b, v_b, eps, fee)
    print_tx(fpay2_b, 'Fastpay 2 tx for State B')
    #####
    opt_close = get_close_opt(TxInput(ft.get_hash(), 0), id_channel, id_a, id_b, v_a, v_b, fee)
    print_tx(opt_close, 'Optimistic close')
    #####
    state_LN_a = get_stateLN(TxInput(ft.get_hash(), 0), id_channel, id_sleepy_channel_a, id_b, v_a, v_b, fee)
    print_tx(state_LN_a, 'LN State tx of A')

def get_ft(input_a: TxInput, input_b: TxInput, id_a: Id, id_b: Id, id_channel: Id, f: int, c: int, fee: int) -> Transaction:
    # deduct 1 times fee, as this is a first level transaction
    tx_out0 = TxOutput(f + 2 * c - fee, id_channel.p2pkh)

    ft = Transaction([input_a, input_b], [tx_out0])

    sig_a = id_a.sk.sign_input(ft, 0, id_a.p2pkh)
    sig_b = id_b.sk.sign_input(ft, 1, id_b.p2pkh)

    input_a.script_sig = Script([sig_a, id_a.pk.to_hex()])
    input_b.script_sig = Script([sig_b, id_b.pk.to_hex()])

    return ft

def get_state(funding: TxInput, id_channel: Id, id_a: Id, id_sleepy_channel: Id, id_exit: Id, v_a: int, v_b:float, c: int, fee: int) -> Transaction:
    # deduct 2 times fee, as this is a second level transaction, spending from f + 2 * c - fee
    tx_out0 = TxOutput(c - fee, id_a.p2pkh)
    tx_out1 = TxOutput(v_a, id_sleepy_channel.p2pkh)
    tx_out2 = TxOutput(v_b + c - fee, id_exit.p2pkh)

    state = Transaction([funding], [tx_out0, tx_out1, tx_out2])

    sig_ft = id_channel.sk.sign_input(state, 0, id_channel.p2pkh)

    funding.script_sig = Script([sig_ft, id_channel.pk.to_hex()])

    return state

def get_slowpay(state: TxInput, id_sleepy_channel: Id, id_receiver: Id, v_a: int, t: int, fee: int) -> Transaction:
    # deduct 1 times fee, as this is a transaction spending from output 1 of state holding v_a
    tx_out0 = TxOutput(v_a - fee, id_receiver.p2pkh)

    punish = Transaction([state], [tx_out0], locktime=t)

    sig_multi = id_sleepy_channel.sk.sign_input(punish, 0, id_sleepy_channel.p2pkh)

    state.script_sig = Script([sig_multi, id_sleepy_channel.pk.to_hex()])

    return punish

def get_punish(state: TxInput, id_sleepy_channel: Id, id_receiver: Id, v_a: int, fee) -> Transaction:
    # deduct 1 times fee, as this is a transaction spending from output 1 of state holding v_a
    tx_out0 = TxOutput(v_a - fee, id_receiver.p2pkh)

    punish = Transaction([state], [tx_out0])

    sig_multi = id_sleepy_channel.sk.sign_input(punish, 0, id_sleepy_channel.p2pkh)

    state.script_sig = Script([sig_multi, id_sleepy_channel.pk.to_hex()])

    return punish

def get_fpay1(state: TxInput, id_exit: Id, id_aux: Id, id_receiver, v_b: int, c: int, eps: int, fee) -> Transaction:
    # deduct 1 times fee, as this is a transaction spending from output 2 of state holding v_b + c - fee
    tx_out0 = TxOutput(eps, id_aux.p2pkh)
    tx_out1 = TxOutput(v_b+c-eps-2*fee, id_receiver.p2pkh)

    fpay1 = Transaction([state], [tx_out0, tx_out1])

    sig_exit = id_exit.sk.sign_input(fpay1, 0, id_exit.p2pkh)

    state.script_sig = Script([sig_exit, id_exit.pk.to_hex()])

    return fpay1

def get_fpay2(state: TxInput, fpay_1: TxInput, id_sleepy_channel: Id, id_aux: Id, id_receiver: Id, v_a: int, eps: int, fee: int) -> Transaction:
    # deduct 1 times fee, as this is a transaction spending from output 1 of state holding v_a and 1 holding fee
    tx_out0 = TxOutput(v_a + eps - fee, id_receiver.p2pkh)

    fpay2 = Transaction([state, fpay_1], [tx_out0])

    sig_sleepy = id_sleepy_channel.sk.sign_input(fpay2, 0, id_sleepy_channel.p2pkh)
    sig_aux = id_aux.sk.sign_input(fpay2, 1, id_aux.p2pkh)

    state.script_sig = Script([sig_sleepy, id_sleepy_channel.pk.to_hex()])
    fpay_1.script_sig = Script([sig_aux, id_aux.pk.to_hex()])

    return fpay2

def get_close_opt(funding: TxInput, id_channel: Id, id_a: Id, id_b: Id, v_a: int, v_b: int, fee) -> Transaction:
    # deduct 2 times fee, as this is a second level transaction, spending from ft holding v_a+v_b - fee
    tx_out0 = TxOutput(v_a - fee, id_a.p2pkh)
    tx_out1 = TxOutput(v_b - fee, id_b.p2pkh)

    close = Transaction([funding], [tx_out0, tx_out1])

    sig_channel = id_channel.sk.sign_input(close, 0, id_channel.p2pkh)

    funding.script_sig = Script([sig_channel, id_channel.pk.to_hex()])

    return close

def get_stateLN(funding: TxInput, id_channel: Id, id_sleepy_channel: Id, id_b: Id, v_a: int, v_b: int, fee) -> Transaction:
    # deduct 2 times fee, as this is a second level transaction, spending from ft holding v_a+v_b - fee
    tx_out0 = TxOutput(v_a - fee, id_sleepy_channel.p2pkh)
    tx_out1 = TxOutput(v_b - fee, id_b.p2pkh)

    state = Transaction([funding], [tx_out0, tx_out1])

    sig_ft = id_channel.sk.sign_input(state, 0, id_channel.p2pkh)

    funding.script_sig = Script([sig_ft, id_channel.pk.to_hex()])

    return state

if __name__ == "__main__":
    main()
