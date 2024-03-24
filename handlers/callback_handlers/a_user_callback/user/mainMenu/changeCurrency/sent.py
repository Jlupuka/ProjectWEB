from typing import NoReturn

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.user_commands import UserAPI
from databaseAPI.tables import Submissions, Users
from lexicon.lexicon import (
    botMessages,
    backLexicon,
    sendMission,
    changeStatus,
    revokeButton,
)

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory, MissionCallbackFactory

from services.userService import UserService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "sent"),
    StateFilter(
        FSMFiatCrypto.money_sent, FSMCryptoFiat.money_sent, FSMCryptoCrypto.money_sent
    ),
)
async def create_mission_FC(
    callback: CallbackQuery, state: FSMContext, bot: Bot
) -> NoReturn:
    state_data: dict[str:str] = await state.get_data()
    walletCurrency: str = state_data["WalletCurrency"]
    currency_to: str = state_data["currency_to"]
    wallet_requisites: str = state_data["user_requisites"]
    wallet_id: int = state_data["walletId"]
    amount_to: float = state_data["amount_to"]
    amount_from: int = state_data["amount_from"]
    work_wallet: str = state_data["work_walletRequisites"]
    user_obj: Users = await UserAPI.select_user(callback.from_user.id)
    admin_obj: Users | None = await UserService.random_admin()
    type_trans: str = state_data["typeTransaction"].replace("-", "/")
    mission_obj: Submissions = await SubmissionsAPI.add_application(
        user_id=user_obj.Id,
        address_id=wallet_id,
        currency_to=currency_to,
        amount_to=amount_to,
        amount_from=amount_from,
        typeTrans=type_trans,
        address_user=wallet_requisites,
    )
    await callback.message.answer(
        text=botMessages["createMission"].format(
            mission_id=mission_obj.Id,
            user_requisites=wallet_requisites,
            amount=amount_to,
            currency_to=currency_to,
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back="main", back_name=backLexicon["backMainMenu"]
        ),
    )
    if admin_obj:
        sendMission_copy = {**sendMission, **revokeButton}
        await bot.send_message(
            chat_id=admin_obj.UserId,
            text=botMessages["sendMission"].format(
                currencyTo=currency_to,
                walletCurrency=walletCurrency,
                missionID=mission_obj.Id,
                adminID=mission_obj.AdminId,
                userID=callback.from_user.id,
                workWallet=work_wallet,
                userRequisites=wallet_requisites,
                amountFrom=amount_from,
                amountTo=amount_to,
                statusMission=changeStatus[mission_obj.Status.lower()].upper(),
                dataTime=mission_obj.DateTime,
            ),
            reply_markup=await Factories.create_fac_mission(
                MissionCallbackFactory,
                mission_id=mission_obj.Id,
                back="main",
                back_name=backLexicon["backMainMenu"],
                sizes=(2, 1),
                **sendMission_copy,
            ),
        )
    await state.clear()
