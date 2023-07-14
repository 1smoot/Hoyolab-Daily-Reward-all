const { GamesEnum, HonkaiImpact, GenshinImpact, HonkaiStarRail, Hoyolab, LanguageEnum } = require('@vermaysha/hoyolab-api')
const axios = require('axios')

const friendlyGameName = {
    'bh3': '붕괴3rd',
    'hk4e': '원신',
    'hkrpg': '붕괴: 스타레일',
    'nxx': '미해결사건부',
    'nap': '젠레스 존 제로',
}

// script:check = document.cookie.includes('ltoken') && document.cookie.includes('ltuid') || alert('Please logout and log back in before trying again, cookie is currently expired/invalid!'); cookie = document.cookie.match(/(ltoken|ltuid|cookie_token|account_id)=\w*/g).join('; '); check && document.write(`<p>${cookie}</p><br><button onclick="navigator.clipboard.writeText('${cookie}')">Click here to copy!</button><br>`)

async function main() {
    const cookies = process.env.COOKIES.split('\n').map(x => x.trim()).filter(x => x.length > 0)

    for (const cookie of cookies) {
        try {
            await prepareUser(cookie, LanguageEnum.KOREAN)
        } catch (error) {
            console.error(`에러: ${error.message}`)
        }
    }
}

async function prepareUser(cookie, lang) {
    const hoyolab = new Hoyolab({
        cookie,
        lang
    })

    // Fetch all user game accounts from all servers
    const games = await hoyolab.gamesList()
    for (const game of games) {
        console.log('====================================================')
        console.log(`${friendlyGameName[game.game_biz.split('_')[0]]}(${game.region_name}) - Lv.${game.level} ${game.nickname}(${game.game_uid})`)
        await claimDailyReward(cookie, game, lang)
        /* redeem = new RedeemModule(
            req,
            LanguageEnum.KOREAN,
            game.game_biz,
            game.region,
            game.game_uid,
        ) */
    }
    console.log('====================================================')
}

async function claimDailyReward(cookie, game, lang) {
    let biz;
    switch (game.game_biz) {
        case GamesEnum.HONKAI_IMPACT:
            biz = new HonkaiImpact({ cookie, lang, uid: game.game_uid })
            break
        case GamesEnum.GENSHIN_IMPACT:
            biz = new GenshinImpact({ cookie, lang, uid: game.game_uid })
            break
        case GamesEnum.HONKAI_STAR_RAIL:
            biz = new HonkaiStarRail({ cookie, lang, uid: game.game_uid })
            break
        default:
            console.log(`Unknown game_biz: ${game.game_biz}`)
            return
    }
    if (!biz?.daily) return

    const result = await biz.daily.claim();
    if (result.code === 0) {
        result.status = '출석 체크 완료!';
    }

    console.log(result.status);
    console.log(`보상: ${result.reward.award.name} x${result.reward.award.cnt}`);
}


main()