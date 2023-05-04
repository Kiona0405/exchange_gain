#! /usr/bin/env python3
import logging
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


def to_float(number: str):
    if number == '-':
        return np.nan
    else:
        return float(number.replace(',', ''))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding='shift_jis')

    # ------------
    # preprocess
    # ------------
    for col in [
            '受渡金額（受取）',
            '受渡金額（受取）[円換算]',
            '受渡金額（支払）',
            '受渡金額（支払）[円換算]']:
        df[col] = df[col].apply(to_float)
    for col in [
            '受渡日',
            '約定日']:
        df[col] = df[col].apply(lambda x: datetime.strptime(x, '%Y/%m/%d'))
    # NOTE csv file is already sorted. Just reverse
    df = df.iloc[::-1]

    # ------------
    # main
    # ------------
    history_dollar = [0]
    history_yen = [0]
    history_exgain = [0]
    history_my_rate = [-1]
    history_actual_rate = [-1]
    for _, row in df.iterrows():
        if row['決済通貨'] != '米ドル':
            logger.error('米ドル以外での決済が検出されました')
            logger.error('スキップします。')
            logger.error(f'info = \n{row}')
            continue

        dollar = history_dollar[-1]
        yen = history_yen[-1]
        exgain = 0
        my_rate = history_yen[-1] / history_dollar[-1] \
            if history_dollar[-1] != 0 else -1
        now_rate = row['為替レート']

        op_type = row['取引区分']
        if op_type in ['外株配当金', '米国株式売却']:
            dollar += row['受渡金額（受取）']
            yen += row['受渡金額（受取）[円換算]']
            if row['口座区分'] == '一般口座':
                logger.warn('--------------')
                logger.warn(f'一般口座での{op_type}が検出されました。')
                logger.warn('為替差益とは別に譲渡益税の申告が必要です。')
                logger.warn(f'info = \n{row}')

        elif op_type == '振替入金':
            dollar += row['受渡金額（受取）']
            yen += row['受渡金額（受取）[円換算]']

        elif op_type in ['米国株式購入', '米国株式積立購入', '振替出金']:
            dollar -= row['受渡金額（支払）']
            yen -= row['受渡金額（支払）'] * my_rate
            exgain = (now_rate - my_rate) * row['受渡金額（支払）']
            if row['口座区分'] == '一般口座':
                logger.warn('--------------')
                logger.warn(f'一般口座での{op_type}が検出されました。')
                logger.warn('為替差益とは別に譲渡益税の申告が必要です。')
                logger.warn(f'info = \n{row}')

        else:
            raise ValueError(f'unkonw op_type = {op_type}')

        history_yen.append(yen)
        history_dollar.append(dollar)
        history_exgain.append(exgain)
        history_my_rate.append(my_rate)
        history_actual_rate.append(now_rate)

    df['yen'] = history_yen[1:]
    df['dollar'] = history_dollar[1:]
    df['exgain'] = history_exgain[1:]
    df['exgain_cumsum'] = df['exgain'].cumsum()
    df['my_rate'] = history_my_rate[1:]
    df['actual_rate'] = history_actual_rate[1:]

    df.to_csv(args.output)
    logger.info(f'result is saved at {Path(args.output).resolve()}')

    logger.info('successfuly done')
