# -*- encoding: utf-8 -*-

###################################################
#module run in different context then e2iplayer, must have separate version checking and assigments
import sys
if sys.version_info[0] == 2: #PY2
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    import SocketServer
    from urlparse import urlsplit, urlparse, parse_qs, urljoin
else: #PY3
    from http.server import SimpleHTTPRequestHandler
    import socketserver as SocketServer
    from urllib.parse import urlsplit, urlparse, parse_qs, urljoin
###################################################
try:
    import json
except Exception:
    import simplejson as json

import base64
import os
import traceback
import urllib
import signal

def signal_handler(sig, frame):
    os.kill(os.getpid(), signal.SIGTERM)

signal.signal(signal.SIGINT, signal_handler)

def updateStatus(pType, pData, pCode=None):
    if isinstance(pData, bytes):
        pData = pData.decode()
    obj = {'type': pType, 'data': pData, 'code': pCode}
    sys.stderr.write("\n%s\n" % json.dumps(obj).encode('utf-8'))

def redirect_handler_factory(url):

    if 'e2itcf' in url:
        job_type = 'cloudflare'
    else:
        job_type = 'captcha'
    to_write = '''
<!doctype html>
<html>
    <body style="background-color: #c8dee1">
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMMAAABOCAYAAACdUaKsAAAACXBIWXMAAAuJAAALiQE3ycutAAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAAHShJREFUeNrsXWl0ZFW1/vauStKZuu2JHqCZZEZ4QCOjyJLBERARBBFdKqI4P0GfOD71OTxRweEtHEAFFRFUVHzwcGBQEUWZBFFBBgEZmqandNKdrqTO936cva2dSyWddFPppFN3rVpJqm5unXvu/s7e+9vDEZJ4ug8RQfMYfnrCTym8xzo/2Zyypx6NkNtyc1obLvj+UgClws/4WRR+AkgAqvYz/t4ESIOOJhgaBwC1+S0BaAm/j6QtUNAM8e/BwiuCo3k0wTDhQOAAaAmvONcdAGYAmA1gFoBue68cVvwKgLUAVgBYBmA5gNUA1oXnlQAM2LkOjKbGaIJhQoCgZHPZCqDNQEEAnQAWAtgVwK4i8kwAiwDMF5EZdm69ZzAAoI/kcgD/JPkggL8D+DOA+wEste+YFkBRaWqLjXyQTQd6ozVBi4FgWgDGQgDPBnCoiCwWkW1FZKMWHpIg2QPgbyRvAHADgDtNa4iBot9+Dm7umqIhctsEwwb7BGVb2acFp3gHAC8UkaNFZDcR0ToPcC3JpQAeB7CSZK8JMACoiEwD0AVgrmmQWfWuQ3KVgeIKA8aTNg43swaC890EQxMMDTOJWgwErfbetgCOE5ETTAvEh1YheS/JO8zMeQDAE+YT9AehLV6/C8AcAFsC2FFE9gDwLBFZULj+YErpBgCXALgOwCr7aK35GYObIyCaYNi0h6/+beb0AsBMAMeIyOtFZBe/b1u57yX5G1u1/2oA6C8IPuuwRzH+wODbdZu/sRjAoaq6v/kdERRXAbgAwC3mPwwELVHdnMymJhg2rVnk2mCavb8XgHep6gsKILiN5A8B/ArAP211dsGuBsFMqB83cF/EwefOeSl8Ph3AswC8REReoqpz/Z9TSk+S/DKAiwGstO9YY+PYbADRBMOmdZLbA/tzlIicparbBBDcR/LbAK4E8KjLZmB6irGB9Tm4UgBGOTjr7oxPA7A7gJNV9VgRaffxpJT+F8CnjYUCgL4AiNQEQxMMYz3cfu+wn50A3qCq/x4Erz+ldBmAbwC4F7UAWWR2no44QIxitxgw2+yzDgCHAniLqi4WEQfonSQ/AuBG++41Nq5JD4gmGMbfR2gNQJgJ4ExVfYPfX0rpfpKfA/B/YdVdi6cGwxrlv0TTjeZTnK6qp4hIi43xEZIfBPCzYDL1o0a/NsFQoOme1tdmAoQ2A8B8s88vVVWWSiWqKkXklwAOR44pLLBz282EkXEGrFOxCwBsD+A9IvJEqVRiqVSiiCwH8Gb7fJ6dP57jnBxy2wRDXXOkFTltYj6AnQB8KwIBwGXG6sw34eq2VVo30XhLph1mGji3BHCKiNwXAPEEgFeHMXdg+FypJhiaYPhXMK3bBGYbAOcWgHCROa0LbDXumCCrrGuJ6Ta2BQBeJiL3BEA8AOBou7c5qAUMm2BogqGuw9wBYAtbQd8pIpUAhEsA7Gar72wzi0oTyNxw5qvbwLAQwMtF5IEAiJsAHGCAmIla4LAJhiYYnuInzDZBOUZEHgpAuArA3gEI0yaomeExkS4D9EIAr3Yfwu7lewB2tM+7J6P/0Ai5VTSPaHe3mSBtAeAdqrrIJv5OZM7+cWOK+lDLEp1wchKo3V77+zqS55JMIgJVfQWAl9sC0G73POXLE5tgGOoreObp8ap6uFGTK0l+Fjl4VTUgxHwiTFBAVI3u7bOx/iCl9D2SkHy80Uw+CVpOmmBoHm5rVwHsJCKvCYGrbyKnVgA5huD8vNR5TUQNsc60RB+A80n+BQBUdTtjlzrNb2hpgqF5oCDQJ4nItmYe/cGcZq9B9oKaTrO1/dVl73WglrKhGFrwH3ONvAZaGyyARC1Zrwrg7yTPJ1k1QLzMnGnYuEtNMDQPMYHZW0SON61QJXkhgEdMSAbtXI9KdxZe7fa+A8RtcRd+r4P2qHRrAEUjD8+PWmPf+7OU0pUAICLdAI5HpmNdO0xZmSiPg5BxAlxjNNcfQC7PnGOJbj81BqlsQJhnzExLgX2JY+sD8BByTUEZtZLM6KTvYMBbYn9X0PhSzZgwuArApSSfJyLdqnpESmkxgGsNEBVspgVBmxoMzxSRU2ylHByjSdAK4FaSl5nNW+/YSUQORI4SO1/eR/I2ADcBeGyUpoSv1FeTPJ5kGcBfTLhbAMwUkc8AOMzeG07LrgFwF8krkHOBVtp1PSfoOBH5PID7SZ6GXOwTtU6j/Ye1Np5bUkrXlEqlY007HI6czIeC9ppaRyPjDCLybg/2bMhLVe8B8MywskaQnaeqS0f437+JyHuQu1BgBCD6it1ugoJgQ89BjikcHnN9RjHuBOAnAA5C5vK3Q6Zrvxy4/lPsO7vGyTTxNJM5puHeqKoVC8TdDeC5qKWWlKai3JYbOPG0iQWACsn7UKv1HZVmsEqxSjBVAOAwVf2KiOwYzl1BcmXGn8wEMENEdhaRs0m+MKX0ZgD3mNClgtOsQRjL9krBdGqJTEtKqQe5aCc2+yqb9pgrImUREVU9huR8kmch1zd42nUEW1tgpsaTbm0FcDPJW0TkABHZieTeAO4OfkN1qimGcoNXoVZD8RMppS8gB63Wp4LFBL/Pzu+3BzQI4AhV/Y6IzLPr3knyWpL3AOix684QkX1E5PkiskhEDlPVb6eUXotcfumAkCD86wx0zha5nZ0wtOMdANxJ8mz7H0/XbgEwg+T2AI5S1SMk53nvR/I/AHwCOQDWWpj78jgLnfdbqgJYQvLXJA+wlPT9AVy+AeZsEwyjAEMpqNuE3NLkMdSKS2Q9D22d2dne7eGZqvp5A0I1pXSplVcuRa2IxlXobSSvVdXXi8jhIrKfqn7aALE8aAVnefYyU2YJgD+Z4A4XP6gg1zP32qsStMufAfw2pfR3VX2TiJRU9YUppVsB/AhDm4ppQVONi3Vh8+RO8k32XLpFZA+Ss21RkXEgLqaUAy0F4V5pwtY3CjAwrGIDZv68TUR2N1PlMpJfDwLZG1ibslGdvSmls0WkrKqHisjRRiN+LQgiTRD+W0QOIfkoyeOQC+rLhfH44QU8vah1unMt047c9eLLKaXZqnqiiEBEXkDyt3XmZ1OswM4sCYC/kPyriOwnIjuS3A7AXVOVXi2P44q0xmi91aMAQ1EIF4vICbbq/8UYJm+9uBK1KjNfcb0eYS3JC0juLiJzVPUEo0yfQC0INg1Al5kKHSQ7MZT/L5ZrJtNua1GrGvPv7Ufm7FOgL7cAsDNyYlx1FAuIm2VSZ0GpVzoqdearXteNeM6APfvHSP44pTTH5rJ3mP8p+ldah40bqcHBSM9a64CPGH2t+KQDgz/MWHs76hsUkf1FZEvTClcht1hcYSbSujort2uUZ5ijeI2InAhgTwC7IDfcwkZMcr2W8dVg2rUBuJfkrchNxbpIbr0egfDn0RKc2Giu+PzFPkipYG5VC8JUL37hjnTFFo0LSH4ftQTELgO1hLHFcZUKAp7C/VcwtPuHFLRwEejlYE77eymYc7GGvOFtM8cTDHEiOMb/2cq0Qq/Z5atNy6wb4VoVW+lA8mYAJ4rIFiKyC8kbw8T32Qq5N8nH7LppA00YhgfngTWvCW8dxvyI3bqnBaHoDH8P2L1U7X2gFu+QEKuohlV/pBaTcWGqGtslwcdrwdD4S1sY1wxbZMphnpfbeJwQ6A+OuL8X01G875Sf0xWYNk+G7Lfv9usNoMGNDCZ642EJqxIMBMvCZK0PVO58Lw0rk3fC8wexluRZJL9gD/XB8PnTYR5iFCZCRxDGnY3z30tEZtk1KsaY/R65v2oPcuzjVJJ3I3fmOFpEDif5NeSWkyMxVdEMqQA4SETeaovB543omBaAqsiBzeeKyP7IHQQdHBWS9yIH7X4D4GEDbCUsDruLyBkASja+++yedwGwr/mC0/18kg8AuBXA7wyonaglHDasQ+B4+gwVDO0oNxZAPEDySZLXAfhHWAVHY5qtK3D5JTw1ynqPCVnZVqkNNaEii9YeKGAE4YhAaAnPoBvAq0TkdUYJF6/9wpTSaSR/AeDrAF6uqi9OKR1A8gkRea2q7pRS6iV5rc11aT3z5AJ9gqoea2kofzSKtdtW404AJ4jI6cXWmeHYm+QJRnV/AblbiINojQH1ZJuLhwBcD+B1Rn9Pr3dN5uOPBp6rbCxtaOCGLeMFhhJyJHhBUPfFGegPzmgETCvJqyzFYq2ZMWOpJ6iKyKIwx711HMBFyBHiFRbbGC1TJgXbutWER2wl3dc+60XOWVpYmJN2+70TwAecfQoCEf0mqGo7yWNI7kxywN4vk5yHWnxkmq26bjKNpJW8KVl7eH+6mUFe5PRuVX1lYVwMz7BkjBmMnv1SSulzyLXiHreZEf7/QBE5xoKiw96r1VzsR3LvlNJ5AM41q6CEBsVmxiNRDyKyUFXPsVWinhC3kVxC8kwAtwe/wjXKCgNByR7wulGuDAk5MnyITfg/TbNoQSg/JCKvAXAjyVORmwPrMIyNl4e2m4aKHe+8656v8nPte/+GXBx0UGHuPTD5DgeCpQYsJflr5IjwOgDzROQQEdnDBGXnlBLD2GKni1LB0V3fItVakANPEZmG3D7zlaFP1GqS1wP4A2pdvxcAOFhVDxKRNhFpV9X3p5SqAH6IWjdCWGHRQaqq/jfJh6yb+P32bGcAWKyqB4pIq4i0qOo7U0prAXw03POk1QwtIrLTehij3VNKu5CsB4YUhLM6xpXhJSJyhE3+rcgp2QyOYpeIbKeqSCntgJy783AdJz4KUEcAdWvwbRQ5l+lUVX1pEO5rjc6NwukO9THW9MvbQv4KwFfMbHNNWSJ5GcnjzRzqUtWonWKXizgWGQU5US7cnwP6OAdC6M73JbPj+wps0eUppSNF5G2qukhEVETeRvJx5CBmhwEB3l4/pVQh+QMA3zUg+AJXAjA9pXSwiJyuqrsZGLfYLKhVkqttpevB8OkYj5C8yx5sZZgg0Vht+YNU9eM2wb1mb/cE88FXrdjUt63gQBcj0W22GnqcYcDA0W6s17HejNiE+xcArg50YTy2EZETRUTt3J8D+Jg5jR4PoD2nhwF8mWRfSulMVS3XoWbrjXc02ruo+bYXkVe44BoQ/hM5IOfO92CYwz4AV5BcllL6mKouFJHZJF9pzvgQOUspDZL8HwAXGimSwjNx7X8pyTtTSqfbd1y4uVCrK0lebiZKf4G6pAnWSvtZLoABGwCCLgAnquoHRGQbewDfM8bDSyEjfx5X1ZZgl0odzbCHiHyywOt3msM8W0RagwlwE4BPmVYoFeIAQA4m7mznPwLgPNNcFROSgbBaOuN0OcndARz1dJqyBTAcKCI72Lj6SF5k4+oO1DMK/l0Xcvr690m+03ycfVNKe8bzbV5+gtyho89eawK4oi9zO8nTC5RxpVGgGE82qc9s/zV1HOiBQJ2N5mYX2Cqs4YF0WmBukYgcJSIHoZZp+j2S30EtdcOZCa1jW5fqvPev31W12yjBkTQhUkpXA/i4LQDTC04/TQPuFtrZX41cQ5FMe60N4BH73U2aK0ke7s2P6/hhsoFAcGDvGvyEGyy202bPL9XRRNUwp78heYTRpR3IxUxxbpYhp7evtGfRg6du2FIJbFhkjhrakaQ8DiDwh7XcVGY9NilGWOuZUe5DzBeRd9gOOQsxNGXCncGieXYpyUss1rBqBCd+VPECkoPBlh9ClZLsQ95z7Qrj+lfaHK9BLQrr89EhIh5MHABwsz3sdXUeeizOaUfOKbpbRPaqMw4OY/6MBIQ4rm4RWRAYnrkAXoVaGkq9hsWuZdtsHlpCsHErm3s/bjdiwO+nyAzGwOXgMM9h0msGT1XoG+PNOBC2UdVvOzM0UjDJmKnbSP7chGyVrWo9GHv3aRbAcCfJb6CWwj0Q4hg9qKWKuM1fCeZXkcnx+V8T/me4KGtcLPrsu+qZkG3BOR8p+7TY4t6/wzt7Q0RQKpX2AbDPBttgIt0klwUNuNTGXllPAG3cN2gc73SMDUkNpq2inw4U6d8sF/9RE4wYUBu0WMHDZnf3BSCs24AJjtFa2LVuxtCs1ZgL5GaD1xx7P6byKJidsczlcOfPNbNsKYZPfykGB2cVALexQkiLRagxSmvDZyswQTdNmSz7QB+pqsfZLN9uhUL3oZYYVk/NDgQfIa7g2EAwFLXcWnv1Y2jmZhVDt6nSYb63GoiCbhPiKKSDw5giJTt/ZuFazsbMss9KgRxIdbSSEwVzzZRx320ZyTXB9/mDmTaeb1VczWPSXavd6wzkTuD3A7gGwPPD+XE7LTbBMHZV+2/28AaNFfqrCVJPcLij3TsQbO+no/tdvXqGPgNa/zA2+0gsmAJYY5oNVhX3bOQmAp4cV63DsHj7mT1C2WsJtZytrUVkLsk9Adxh5/dj6Ba47lt587B9RGR7E/51yCWtDyHnRkFE1pD8MWrJkX0FQPjYOu3nbBF5r4gcklJaYlo61fFVJhwYJnoRh090lz2sJ0wjrLQH9ghyZugSoy/9p+fmr2uQKk4Ymvk51rx7MSG909MQROT5yCnmaiur92LyfkzT7b3ZyHvKtYYFrYfkXSGw9TLkFJOW8H/xWjPs922R845cDpZbjOM2bzQmIgcjl4RWUOtFqwXa2d8ncsPmw0SkRUT2te+rbARN3gRDOFydwwT9UVuhegIV6/UL45b7jo2rVPP/u9UCjbAioHci77zTYuaOd+eYjVrXvpNV9cjCtQYA/Na0A0RkHwBvsWu0h2v4qxM5T+rNqro4XOths+lvtBgJTKjfYJrLI8+xI2BMkTmq0Jrzdjw18j6hV97xYpOcWUkbIXSDpq5XY2ydNtbHFHEYFmOkz9MYv6cI0ATgQZIXk6xYkOpg5G7fhyEny/lq3omc+Hem1VbXu4fbUkqXu3ZQ1ZMAfAS5vrsLtSj5DOSWkh+1HULd44WlYq9Ezga4IKW0AgBUdUsR+QiA04LGKQdyYEcAZ6jqWRaH8WtdYiYl1zMXU8pn8PyZrmB3r68GuoqhDX4RVHIHhlZTjda0iddksMuj8A8WmI7iOSnYzBzDdxcdT3fqr0wpbaWqbzEqc1+S56SUbjKTcBDALGvpsn0IhsHy3YBaJPfClNKWqvpiu9bRKaV9rf56ic3fViJyQNw7OjjPXjiVAPyC5BdJ/qeBaw7Jd5F8ifWgXWHzuMAqEbcKY1tK8pOodSMZKPhcDatJmPBgsKzVz6IWcBuNELWT/J21gx+06+ykquehFvwZy9EG4PGU0oeRc2xc00S/wpmigbDiDmJoVNxzpUZ7Hwz/M1gAQ6+N64sppbKqvtFs/umlUulIAEfWRVZKfzbqcg97a3UAxEdTSi2qeqQJ8QLkRgj1+E9/PiD5IHIwrD/MyUUpJYjI21V1lo1tJ9NSGGZsD1ge03WmiXz/aYQ5r0w1NinSfW0isvcGXGOONf91B6xLRJ69kcC8zOx0N936jNkBaht8FFeyXgD9Zkr0BkZltGDwksXVdo1BM0dWGU1aBfCplNK9InKq5ysV8/1JrrRkwwsBnEhyD5IViymsMM37IIAzUkqnWhLggmLxjF3rAZItqupR8Jvtf70W2stiv0ryjmq1epqIPEdEuoa53jKS1wD4KnLGbSmAdFWoV1iFWg7alAADAZRJ/jKl5Lw3Mfr0a1+p7zAh/F1K6fxgZiWMLUfFJ/1R259gWmCEVps58A/kPP2HUMta9W55D5L8mHWd+35Y6dIo78XHenFKyYmA39m4VpvgJADfInk9yYOQyz87w7w9ihzsu9uE6bsppdXG5d9s5/TYeJcA+AzJK0geaKxRrGN+FMCTIvIm0wqDyCWbq4Nm8O9tt8/uILkPyX0sNuGkRsXm7Bbk3Ko1ISbhgPpxSqnLrvkTM50m3D7UjdoU3QvanRKchVpAZjRCPBh4/FLg3meO8TpRIPttNe5HrcWLU7duwrQZULzRmbdpTzYWT1fwDn+jsX1jHbebCO5DIdyHF/po+Nu7fVeDaVEu+AnE0GL62M1Qwt/e3tJ7u56oqmeKCFJKfyT5VmOTelFrX18K/1cuxClifUkkRpxZ8sInL7FdF8zV0hhNzWFNvMliJvUHYRjE2HaG8aKeSjCR2lDrfSoboKkGMTQYl8LLU6S9BnoH1GoIPMmuPQj/WNrIF8mA1gD4GKNwoXKmJgU+P0a2I3VcDvcWxxOvVSrcZ8Wc3iMDBfpLi9lUC/5STJgr7jEhBc03WFggiikqrYVnO+EYpUaaSR6p9UjxWGncVDAx+rBxm3sQT02VQIEm7QfwNhH5EHLC3zkAzkGt9UoxyDaWe4nZpPUi1lHw6hXoJKw/a5MFAR3A0E3TXZBPEJE9bYW9D8AvwupdrUMtp6DV6lXQpVHQ1MXirClFrY7FR9iUR3w4AmCZ1fKC5GlGcf7ehKnILG3o96wv7vF03Vds3OX5TruKyKuCVviB+SEJI8eBNiS+MqGFv3g0t7Eq0LkAfmotKD0q/HbkfQtaMfl2xYxaod2Yq9eFXKQ/mUNbDXZ+mqoPvwmGoaue9/n5ZkppOQBY6sMpqCXKtU0SQMS9rb19zUtV9YSwZ903kDuBrE8rNMEwxY4UHPQ/kLwoJL6djrzVU2yFONEBUezjtK+IvF1ESpaa/UPkZl9egz7QBEPzKILBnchvpZSuNe0wQ0Teh1zx5YBonaCAcI3gQCgB2E5EzlLVRWYe3YXcfKAnMHZpyktAI/d0m6SLQxtyZucWAF4kIv/wvdpE5BbkJLqF5kd0YujOnxMBCGVkmniujXNfAFerqt/Dk2b2zbNz2ifjotgQuW2C4SmHxxy2QN6c8DQRWRkAcROA5yF36JhvWmIi7J/sQOhEbZvexQCucCCoagXAeycwmJtgmIBmhgff5iGXL56lqusKGuLFBogFyGnRm8qPkOAfTDeALgDwHAA/D0AggLMBbGPnTMeGBTCbYJhCYHABawnCtTWAD6tqfwDE3QBeY58tQC7E6RxnLRGp05k21oXI+03fXADCl5ALh+Yj10q0YhJvZNgIuW1UbtLmQi54M2GvPT5JRN6vqs8AgJTSKpJfBfAd1HYD8m7izs6kBo/RW7uIgfckETlDVb0d/mBK6Vzk/q2eTj3p2aOGLLpNzTAqenJGMD9OFZGHwgboRO4A8XIzQRaG1bcDQ2uGnw5NEF/uI3Sbo3yxqg4G7bUcwPtMe82zMbVtDixiUzNsWg3h+x4AuaPEB0XkwFDdtdz2RrsMuf28F/J4uavXNMQ2KRyl4MeNBQVD29AMAHieiJyvqtsGQfkryU8gF9nETRk3i3hCQ+S2CYZRA8KjuQ6IrQC8SUROUdWOIIQPkvwRctuXe1Hbew2oJc8Vs0/r7Y4Z933wHqveknEdamnavQBepKqXikiHmUWXIscR7kctqNbQLaCaYJg6YEAQTt/pxnuLPhfAaap6iNVxOCiW2EaK1yNXfj2CWtNlF/p6SWxS53P/3pnIpZ5bI28E8g/UWrS8X0SOIHmeAdFT331j+So2o8BaEwwTg2WKZtM0E8S5yAG6k0VkLwkTYHuTPUjyDgPFvciNtZahtr9DzPuPTvEs8z+2A/AsEXmWlYSWUkr/BeATdl4VtSKc1ajtfRYd+c3KmWuCYeKZTZ7J6o17FyDnML1UVReHlvHxAVasLftjAJaT7Al+RQm5XrzLtMA82yRxWnFOq9XqlQBejVp5pfsiXplX3dy0QRMMk0NLxPRuIKdz7IW8VewBAHYUkfaNnReSFZL32R5olyHXWXjztHoFQ9xcJ78JhskBCq9d9rrtecjF/bsbKBYB2FJEZmL47txV5EYIPcgNvR5G7qF0B3KbmwdMI3gZ5+DmLPhNMExeUJQCMDzG4MX1XmDjbSOno1ag76aWU6A9yO1fnrDf1wSh9/qDCsavnWYTDE0wbBTz5O3lvZC+FMDBAnOEYUybGFcYRP2espxqE9wEw+TWGBEgxSCaFoDgQl7F0G7fxUYGU/aYbK1imkdNaIuNEYrdL2QY55dTXejH8/j/AQDUUE1fJ4VDjQAAAABJRU5ErkJggg=="/>
        <br><br><br><br>
        <center>
            <a href="%s" target="_blank"><button type="Button" style="color: white; font-weight: bold; font-size: x-large; text-align: center; padding: 4ex; border-radius: 20px; background-color:#448844">Get %s job</button></a>
        </center>
    </body>
</html>
''' % (url, job_type)

    with open(os.path.join(os.path.dirname(__file__), "htdocs/e2it.html"), 'w') as html:
        html.write(to_write)

    DIRECTORY = os.path.join(os.path.dirname(__file__), "htdocs")
    print(DIRECTORY)

    class RedirectHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            os.chdir(DIRECTORY)
            SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            elif 'response' in self.path:
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.path.encode())
                parsed_path = urlsplit(self.path)
                query = parse_qs(parsed_path.query)
                token = query.get('token', None)[0]
                updateStatus('captcha_result', token)
                return
            SimpleHTTPRequestHandler.do_GET(self)
    return RedirectHandler

if __name__ == "__main__":
    try:
        if len(sys.argv) < 1:
            sys.stderr.write('Wrong parameters\n')
            sys.exit(1)

        CAPTCHA_DATA = json.loads(base64.b64decode(sys.argv[1]))
        IP = sys.argv[2]
        PORT = int(sys.argv[3])

        returnCode = 0

        siteUrl = CAPTCHA_DATA['siteUrl']
        siteKey = CAPTCHA_DATA['siteKey']
        captchaType = CAPTCHA_DATA['captchaType']

        SocketServer.TCPServer.allow_reuse_address = True
        if captchaType == 'CF':
            httpd =  SocketServer.TCPServer((IP, PORT), redirect_handler_factory('%s#e2itcf_sep_c=%s' % (siteUrl, siteKey)))
        else:
            httpd =  SocketServer.TCPServer((IP, PORT), redirect_handler_factory('%s/#e2it?k=%s&st=%s' % (siteUrl, siteKey, captchaType)))
        print("Http Server Serving at port", PORT)
        httpd.serve_forever()
    except Exception:
        sys.stderr.write(traceback.format_exc())
        returnCode = -1

    sys.exit(returnCode)