"""
胖虫电商系统 - 物流服务
集成快递鸟 API（模拟实现）
"""
import hashlib
import json
import httpx
from typing import Optional, Dict, Any
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class LogisticsService:
    """物流服务（快递鸟 API 集成）"""

    def __init__(self):
        self.app_key = settings.KDNIAO_APP_KEY
        self.app_secret = settings.KDNIAO_APP_SECRET
        self.api_url = "http://api.kdniao.com/api"

    def _generate_sign(self, data: str) -> str:
        """生成签名"""
        # 快递鸟签名规则：MD5(param + app_key)
        sign_str = data + self.app_key
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    async def query_logistics(self, tracking_number: str, shipping_company: str) -> Optional[Dict[str, Any]]:
        """
        查询物流轨迹

        Args:
            tracking_number: 物流单号
            shipping_company: 物流公司代码

        Returns:
            物流轨迹信息
        """
        if not self.app_key or not self.app_secret:
            logger.warning("快递鸟 API 未配置，返回模拟数据")
            return self._mock_logistics_data(tracking_number)

        # 构建请求参数
        params = {
            "OrderCode": "",
            "ShipperCode": shipping_company,
            "LogisticCode": tracking_number,
        }

        data = json.dumps(params)
        sign = self._generate_sign(data)

        request_data = {
            "RequestData": data,
            "EBusinessID": self.app_key,
            "RequestType": "8001",
            "DataSign": sign,
            "DataType": "2",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/dist",
                    data=request_data,
                    timeout=10
                )
                result = response.json()

                if result.get("Success"):
                    return {
                        "tracking_number": tracking_number,
                        "shipping_company": shipping_company,
                        "status": result.get("State"),
                        "traces": self._format_traces(result.get("Traces", []))
                    }
                else:
                    logger.error(f"查询物流失败: {result.get('Reason')}")
                    return None

        except Exception as e:
            logger.error(f"查询物流异常: {str(e)}")
            return self._mock_logistics_data(tracking_number)

    def _format_traces(self, traces: list) -> list:
        """格式化物流轨迹"""
        formatted = []
        for trace in traces:
            formatted.append({
                "time": trace.get("AcceptTime"),
                "location": trace.get("AcceptStation"),
                "description": trace.get("AcceptStation"),
                "status": trace.get("Action")
            })
        return formatted

    def _mock_logistics_data(self, tracking_number: str) -> Dict[str, Any]:
        """模拟物流数据（用于开发测试）"""
        return {
            "tracking_number": tracking_number,
            "shipping_company": "SF",
            "status": "已签收",
            "traces": [
                {
                    "time": "2024-01-20 10:00:00",
                    "location": "深圳市南山区",
                    "description": "快件已签收，签收人：本人签收",
                    "status": "签收"
                },
                {
                    "time": "2024-01-20 08:30:00",
                    "location": "深圳市南山区",
                    "description": "派件中，快递员：张师傅，电话：138****8000",
                    "status": "派件"
                },
                {
                    "time": "2024-01-19 22:00:00",
                    "location": "深圳市转运中心",
                    "description": "已到达深圳市转运中心",
                    "status": "到达"
                },
                {
                    "time": "2024-01-18 20:00:00",
                    "location": "上海市转运中心",
                    "description": "已从上海市转运中心发出",
                    "status": "发出"
                },
                {
                    "time": "2024-01-18 10:00:00",
                    "location": "上海市浦东新区",
                    "description": "快递员已揽收",
                    "status": "揽收"
                }
            ]
        }

    async def estimate_shipping_fee(
        self,
        province: str,
        city: str,
        weight: float,
        amount: float
    ) -> float:
        """
        估算运费

        Args:
            province: 省份
            city: 城市
            weight: 重量(kg)
            amount: 商品金额

        Returns:
            运费金额
        """
        # 满额包邮
        if amount >= settings.FREE_SHIPPING_THRESHOLD:
            return 0.0

        # 固定运费
        return settings.SHIPPING_FEE


# 创建全局物流服务实例
logistics_service = LogisticsService()


# 物流公司代码映射
SHIPPING_COMPANIES = {
    "SF": "顺丰速运",
    "YD": "韵达快递",
    "YT": "圆通速递",
    "ZT": "中通快递",
    "ST": "申通快递",
    "EMS": "EMS",
    "JD": "京东物流",
}


def get_shipping_company_name(code: str) -> str:
    """获取物流公司名称"""
    return SHIPPING_COMPANIES.get(code, code)
