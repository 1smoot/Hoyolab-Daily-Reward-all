import genshin
import asyncio
import os
import patches
import sys

friendlyGameName = {
    genshin.types.Game.HONKAI: '붕괴3rd',
    genshin.types.Game.GENSHIN: '원신',
    genshin.types.Game.STARRAIL: '붕괴: 스타레일',
    'nxx': '미해결사건부',
    'nap': '젠레스 존 제로'
}

async def main():
    failedJobs = []
    assert 'COOKIES' in os.environ, 'COOKIES secret이 지정되지 않았습니다!'
    for context in os.environ['COOKIES'].split('\n'):
        user = dict(item for item in parse_cookies(context))
        if 'ltoken' not in user or 'ltuid' not in user:
            print('ltuid 또는 ltoken 값이 존재하지 않음, 혹은 COOKIES secret 작성 형식이 잘못되었을 수 있습니다.')
            continue
        client = genshin.Client(user, lang='ko-kr')
        accounts = await client.get_game_accounts()
        print('====================================================')
        for account in accounts:
            if account.game not in friendlyGameName:
                continue
            print(f'{friendlyGameName[account.game]}({account.server_name}) - Lv.{account.level} {account.nickname}({account.uid})')
            result = await claim_daily_reward(client, game=account.game)
            if result is not None and result[0] is not None:
                if result[1] is True:
                    print('출석 체크 완료!')
                else:
                    print('이미 출석 체크된 계정입니다.')
                print(f'보상: {result[0].name} x{result[0].amount}')
            else:
                failedJobs.append(f'{len(failedJobs)+1}) [{friendlyGameName[account.game]}({account.server_name})] Lv.{account.level} {account.nickname}({account.uid}): {result[2]}')
                print('출석 체크에 실패했습니다.')
            print('====================================================')
    if len(failedJobs):
        print('출석 체크에 실패한 계정이 있습니다:')
        for error in failedJobs:
            print(error)
        sys.exit(1)
    

def parse_cookies(cookies):
    items = cookies.split(';')
    for item in items:
        kv = item.strip().split('=')
        if len(kv) != 2:
            continue
        if(kv[1].isnumeric()):
            kv[1] = int(kv[1])
        yield kv

async def claim_daily_reward(client: genshin.Client, game):
    try:
        signed_in, claimed_rewards = await client.get_reward_info(game=game)
        reward = await client.claim_daily_reward(game=game)
    except genshin.AlreadyClaimed:
        assert signed_in
        rewards = await client.get_monthly_rewards(game=game)
        return rewards[claimed_rewards-1], False, None
    except genshin.AccountNotFound:
        assert not signed_in
        return None, False, '계정을 찾을 수 없습니다.'
    except genshin.GeetestTriggered:
        print('GeeTest(CAPTCHA) 요구됨')
        return None, False, 'GeeTest(CAPTCHA) 요구됨'
    except Exception as e:
        print(e)
        return None, False, e
    else:
        if not signed_in:
            signed_in, claimed_rewards = await client.get_reward_info(game=game)
        if reward is None:
            rewards = await client.get_monthly_rewards(game=game)
            reward = rewards[claimed_rewards-1]
        assert signed_in, 'COOKIES secret이 잘못 지정됐거나, 로그인 정보가 만료되었습니다. HoYoLab에 다시 로그인한 후 COOKIES secret을 다시 지정해주세요.'
        return reward, True, None
        

if __name__ == "__main__":
    asyncio.run(main())
