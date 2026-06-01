export function getPaymentRedirectUrl(paymentResponse) {
  const paymentUrl = paymentResponse?.payment_url

  if (typeof paymentUrl !== 'string' || paymentUrl.trim() === '') {
    throw new Error('支付链接无效，请稍后在订单详情中重试')
  }

  try {
    return new URL(paymentUrl, window.location.origin).toString()
  } catch {
    throw new Error('支付链接格式无效，请稍后在订单详情中重试')
  }
}

export function redirectToPayment(paymentResponse) {
  const redirectUrl = getPaymentRedirectUrl(paymentResponse)
  window.location.assign(redirectUrl)
  return redirectUrl
}
