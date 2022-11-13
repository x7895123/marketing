import bcrypt

from shared.settings import Settings
from iou_service.full_service import FullService
from iou_service.lite_service import LiteService
from services.iou_db import Db as IouDB


def main():
    settings = Settings('test')
    iou_service = FullService(settings=settings, logger=logger)
    logger.info('Start iou_api_test')

    logger.info(f"iou_api.aqua {iou_service.aqua.address}")
    logger.info(f"iou_api.aqua {iou_service.x3.address}")

    token = iou_service.get_auth_token('01kz', '1')
    print(token.body)
    #
    # iou_db = IouDB(logger)
    # iou_db.check_access_token('d25cccb6-ca33-4fae-822e-5f4d94a72ba2')

    # deal_address = create_gift('aqua', iou_api.x3.address, [2], [77], 'iou_api_test')
    # blockchain.print_event(set_approve_for_all('aqua', deal_address))

    # iou_api.create_gift2(iou_api.aqua, [25], [1], iou_api.x3.address, 'Good News!!!')

    # iou_api.approve_for_all(iou_api.aqua, '0x06a43497eec0853d5873a0bf65400fc98a841b30', True)


if __name__ == '__main__':
    main()

