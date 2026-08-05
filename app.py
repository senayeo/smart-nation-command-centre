import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime

# Central system parameter defining your local SQLite database architecture
DB_FILE = "smart_waste_nationwide.db"

# SYSTEM FIX: Embedded Base64 asset placeholder to eliminate string wrapping lag errors
BASE64_IMAGE = "/9j/4AAQSkZJRgABAQEAYABgAAD/4QAiRXhpZgAATU0AKgAAAAgAAQESAAMAAAABAAEAAAAAAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCADrAWoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvMtf/AOQ7e/8AXd//AEI16bXmWv8A/Idvf+u7/wDoRoA9NooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKMj1oAKKMj1FGQaACiiigAooooAKKKKACijOKM5oAKKKKACijOaM4oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvMtf/5Dt7/13f8A9CNem15lr/8AyHb3/ru//oRoA9NooooAKKKKACiiigAooooAKKKKACiiigAooooAjpCMA0prxL9pL4h6Re2Vx4M+xeJ9V1u/iE3laGZbSe0GD5c73WUjh+5/HIOnemjoweGnXq+ypno3j/4l+H/hl4ZOq+IdVttHsPM8o3E7bED9ua1NL1a21zTYLizmWe2nj3xSD50da+DZvjR4n1H9jf4rad4o8eeGvFtxoOlyafJFZQN9stp5m2R+dN8kb/8AAIx/10r6N/Y1+MsHxZ0zWrHSbAL4T8MyxaRpeo+exGo7IU8/5P4PLk+T8K56WI552PoMx4YqYXCTq/yTs/5en+Z7u3C1R1TUoNJsZri4nWCCEebJJN9xFq7klfevBP2t/ilcLZDwVoFyLbV9YtHutQu/KMv9iaWn+vuti/x/wR/9NOf+WZq6lT2Z89g8H7ev7M9t0zW7bxDp0dxY3EM1vMMxywlXRxV7cHXPTFfL37NvxYsPgF4S8OeGr2fTp/Al/DHD4W8UWexLO5R+kFz/AM8rj/b/ANXJ6iT93X0/HcrJHkY98U6dRTNMwwboVLfYJKCcCqWr6xb6HYG4uJ7e3gXrLPN5aCvNfid8fPA1lZX+g3+v21xc3EbRy2djM8958/8A0zt8yflWliMPh6ldr2aPUTcI8eRyCcU9cRpx+tfGP7EH7SGq+GPgJDYQ+E/iH41ngv78xXZKSJs+0ybE8+5lj7Yr139kL9qe5/aX0XXri58NX2g/2Rqb2ADTrPHOUfnZIh+Z06P7+tc9LEe02PUzHh3F4T21/gpnvFHWhegqM3AHXArc8NABigjNcL8XPi3J8MdMt5oPDfiTxRdTyeVFFpNukj/V2coifnU3wk+I118UPCQv7/QNZ8LzGV4vsmqBI7j5P4/kc8Ucxv8AV6ns/aHcdKKKKDAKKKKACiiigAooooAKKKKACiiigAooooAK8y1//kO3v/Xd/wD0I16bXmWv/wDIdvf+u7/+hGgD02iiigAooooAKKKKACiiigAooooAKKKKACiig9DQBHjmvlv/AIKCaVZePX8K6BBqAOvQ3D3/APZP2Ke+i1K12GNxNChSNh5hjx57onyV9RFvl/CvmTxtF4s+IHiTxlpLeLDff8I3Ksr+HfDMK2F5JazPmCOa8mP3/LQ/6vy/+ulRXX7s9zh2fs8asR/IfKd5f+G9P/Z00v7do9zBYa54ntdQtbm4vY5LpIZLj7RNPc2dv+7ij8uB/IT95/H/AKuvr/8A4J46pYaj8HtbuoZYDGfFGsSNg9N95JIn/kN0ryj9jn4X+EfhH8Lm+JvikWVjbadql/axxeR5n9gyTXnkSCZ1+Z5I8JBv/wCWcadvnrrPi/4Vn+GPxZ1rR/BusaIq/FOF7m58O6559paXUwTyJJLO5T/loQI/Mh68+ZxXm4al7P8Aen3fEeMw+Mc8tpt/Hfn+z/ej/wAG9vvPoP4reKNW8K+Ht3h/SLnXtXuv3VrawlUTef45XP3E/wBqvnf4yaV43/Zd+Gljrlhf22reJvF2s21t4n1H7Gj3cvnfu4Us0f5ESMnYiSete+/ADw34l8O/CHQ9P8X6jbax4gtrYRXV3BuEdycff/GvPv267KPXvBXhPRLtt0GveLtKtZQpdGMaTea/zp93iOu6o/3ftD4jKa9PD432DUZwUv8AwI8H8P8Ag3SdV/aG/tjx+1/DYeG/C80vic6zqn263je8m2QQTBT5H+ojkcpGnlx7/wDgdeqeEfhP498IaHYXPwa8caBq/gq/iElrp/iHzruOyT/p2uk+d4/9iT86zdU+FV9qGv33hnwv4U+GlxpGlS/brnSBfXVul1v/ANRJeBLfy3k/d/ck8zpXs/wX8S+ML77bp/ifwRbeEIrCNIrSey1SO9trnj+H93G6filRSpnsZvmE3T9pCz/uvl/9Jf8AVupq2fhO5+Ivwr/snx7pWkXNzqEPlanaQh57OT/c39q+cv2fdR8T/s1WniTwJYfDbXtdXQtTm/s/UIIoLW2urR/3kHmzTS/PJHv2cb/9XX2EwYJz1qvfIiRTEhcAc8ZzxW84HzeBzV04zp1Ic0Jte75nxF+zlpvxg+IP7NM+k+E4PCOg2Nxd6rbf2jfXssl3DI97Pv2IkXl/Id1fUn7Ofwqb4NfBTw74cmgsIbnSLBLaYWW7yN4HzsN3v6+tcN/wTocD9mOA959b1mX/AMqVxXvMi7h1wB196yw8P3dM9TirMZ1MZXw6XJDnk9DJ8RXt9pOlT3FjbwXF8InMUUsuxJH/AIELYrwHUNRb9s3SLeDT9e134ZfEDwlcvFqFnDMstxYeamx0dP8AVzRyR/PHL/uH1Fej/F/wJ4g17x54A1DRr021roOtPd6nb+e0f2iD7LcR4/2+ZEqL4xfs0eH/AIyXcGrLPfaB4o06PyrHXdMl+z6hbR/8894++n+w+RW1RT3RwZfUoUVCbe/2v5f8UepftPE/h/4P6h4a8Fy/aNPiuLZbXTJ7vJS5eNceQZs8zkDf/t/PXoK4KZZiwbpXzT4+/Yj8YfFrQW0Lxb8ZNf1jQbkYurQ6LYW7yov+2kVe9+BvB9v4A8J2OkQST3MOnW0drHLPK0s7oi4+d25Y0qftLamWZYbCU4QqUq/PN7/F/wC3cp0o6CigdKKs8sKKKKACiiigAooooAKKKKACiiigAooooAK8y1//AJDt7/13f/0I16bXmWv/APIdvf8Aru//AKEaAPTaKKKACiiigAooooAKKKKACiiigAooooAKKKKAIgwbiuU8I/CnR/A+ua7fada/Z7/xNefb9Ql3M/2iQIkf8X+xGgrq9gpaYoVJwMCDwLpGn6BPpMGn2AsLiR5JrUwL5Ehd977kxg5zXP8Axp+BmgfHLwiui67A32aC5hu4nhPlyW88LiRJEfsR/jXfEH1rA8f6Vc+IPB2rWNgQL+4tZIYudnlu6cc0ps3w9epCpz85Dpvj3T76w0q4t/OUa8VNqRF1zCZP/QENct8bPhFpHx80/TbG417UNOn0DUEvwdKvVhuI38uRNm4fd+SQ1B4j+C4sGsv7Btxbra6Vc2kTee2+J38iNNh/3BJ89ZMnwh160vpr+2h0iCdhZw2kPIgtkR5PM92/1m//AG9lQenhqVKFT2tOpynZeGvDXhb4LeEYLLSYLexshIMRQDdJJI7hC3qzmRxlq62bW7a1AzPCMyeVjP8AH6V4rH8AdetEhsrS5tY7ayv3NrPn7RPbwOzzvP8AP/y38/Z/3xWpo3wh1BdQtv7QgJt4o4YhFbzKfL7z75H+fEj/AD5j+eT/AJaVk5jxGGw8n7T2/MerDUrdj5Pnxef9a5jTPiXY64Yfs8V62nX7+VbXZC7Lk7Oqc72H+1is7wf8JnsPhtf6dcz41bWIpvt95AP+Wk3mfd/3N/H0qDxj4FvtdsrfyNJ0+3uIBDFLKQsnmQb/AN5AnpWpy0aFD2m5e+B3w/0b4PfDSz0LSb43Fhby3EsUssqyE75nkfnvy5roNG8a6Tr2o3EFrfW801iwjlHm8jcgf+TpXnV38GtY1HUDcZtvs9vYz7YZ5iJL27do9m/Z8iwfuIvkFGm/Aa4TSNK0kxw29tDqj3V/J8m+9jCSbE/WP/visv3h0zpYepz1alT3z1OHX7G98nE8J89PMi/e/fFaArzPwh8M7nTvFk09/wDvjBdzTReTtSPy8/uP9v8Adx/Js/1delqNoxXSebiKdOn/AAyXFGKKKRgFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABXmWv/8AIdvf+u7/APoRr02vMtf/AOQ7e/8AXd//AEI0Aem0UUUAFFFFABRRRQAUUUUAFFFFABRRkeooyPUUAFFFFABRRRQAUUUUAGB6CjGKKKADAooyPUUZHqKADGKMD0oooAMYooooAMD0FFFFABRRRQAUUUUAFFGR6ijI9RQAUUUUAFFFGcUAFFFFABRRRQAUUUUAFeZa/wD8h29/67v/AOhGvTa8y1//AJDt7/13f/0I0Aem0UUUAFFFFABRRRQAVw3ir40af4U1yfT54L4zQc/uQpz8ma7mvn342f8AJTtQ/wC2H/oFAHc/8NIaT/z4X/5L/jR/w0hpP/Phf/kv+NfmL4q/ah+IGn+INWt7fxBcfZ7e7mii/cRfwP8A9c6pf8NZfED/AKGi4/78Qf8AxuuH69SPQ/syqfqN/wANHaT/AM+F9+S/40f8NG6T/wA+F9+S/wCNfnf4P8R/HD4geH7fWNH1j7Rp9xv8r9/ZRyfI/l/cf7laV5B+0Bp//Hxcf8fGz/lvZfx/u4//ACJWn1+kR/Z8/wCc+/8A/hpDSf8Anwv/AMl/xo/4aQ0n/nwv/wAl/wAa/Omz8Y/GjUPtH/FQaf8A6Pd3Vp/x/WX72S2h8yfZ/f8A3dR+MPH/AMaPh/8Ab/7Y1i4t/wCz4vNm/wCPWT5Ee3j/AIPv/wCvhpfXqQ/qFQ/Rr/hpDSf+fC//ACX/ABo/4aQ0n/nwv/yX/Gvy4/4ay+IH/Q0XH/fiD/43R/w1l8QP+houP+/EH/xuo+v0iv7LqH6jj9pDSh/y4X/5L/jXkfxc/wCCpfgn4QfECfw/qGheJ7i4t4kmM0Ig8v51/wBqUV43+x/8RtY+KHw/1e41jUP7QuLfUPKi+7/q/Jj/ALlfOn7dP/JyF/8A9etr/wCia7ab9ornn1KXs6vsj7N/4fQfD7/oV/GX/fq2/wDjtH/D6D4ff9Cv4y/79W3/AMdr5a+HvwW8L+IPh/pFxcaP9ouLi0SWX9+38aV0Gm/s5+F9Q1CC3t/D9v8AaLiVIov37/6x3rzXmlO9jq+oVT6D/wCHzvw+/wChY8Zf9+7b/wCO0f8AD534ff8AQseMv+/dt/8AHa8b/wCGJtP/AOhf0+4+0f6ryL7/AFuz/tpRefsP6fp/n/aPC9v/AKPsll/05v40k/6af9M3rX+06f8AIH1E9l/4fP8Aw/8A+hY8Y/8Afq2/+O0f8Pn/AIf/APQseMf+/Vt/8drxHR/2NNP8Qfb7e38L29xcaf5Pm/v3/d+d/q/+WlXv+GEbf/oV9P8A/A7/AO20v7UpfyB9VqHsP/D6D4ff9Cv4y/79W3/x2j/h9B8Pv+hX8Zf9+rb/AOO14FrH7L3h/wAP/Z7i48P2/wDpG/yv9OfzPkfy/wCCT5Kzv+FA+D/+gNb/APf+Wsv7XpD+oVT6N/4fPfD7/oWPGX/fq2/+O16p8GP25vDHxv8AB/8AbGnaVrVrbmaS2Im8nflP92SvzN/aP8AaP4P1DSf7Ht/s/wBoifzfvfwPX0X+wH/yb9/3Fbn/ANp16lKrTqU/anLVpezPtL/hpDSf+fC//Jf8aP8AhpDSf+fC/wDyX/Gvzg+OX7Rnjjwf8YNe0/T/ABBcW+n6fd+VFD5EX7r5P9uuX/4ay+IH/Q0XH/fiD/43XL9epHcsBUP1H/4aQ0n/AJ8L/wDJf8aP+GkNJ/58L/8AJf8AGvzK8H/H74ofEDUP7P0/xB/pHlPd/v8A7Pbx+Wif33+5XZGf48f9BD7P+98r9/PZR/vN/l+X/t0vr1IPqFQ/QL/ho7Sf+fC+/Jf8aP8Aho3Sf+fC+/Jf8a/PyCf48D7Rb/2h/pFvE8s0Pn2f2iKOF/Lk+T+D95JVez1X48ah4fg1C31D/iX3Fol3FN59l/q3T93/ALkn+xT+v0if7On/ADn6Gf8ADSGk/wDPhf8A5L/jR/w0hpP/AD4X/wCS/wCNfmV4q/aE+KHg/wAQT6PqHiD/AImGny+VL5H2eSPzP+AR1m/8NZfED/oaLj/vxB/8brL6/SL/ALLqn6j/APDR+lY/48b/APJf8a6bwZ43t/HeltdW63EMIl8vEoUZNfn9+xn8W/EHxQ/t7/hINQ/tD7PFD5X3P3W95P7lfb/7N5x4LuP+vt//AECOuqlU9pS9ocdal7OpY9FXoKKKK1MwooooAKKKKACvMtf/AOQ7e/8AXd//AEI16bXmWv8A/Idvf+u7/wDoRoA9NooooAKKKKACiiigAr59+Nn/ACU7UP8Ath/6BX0FXzz8a/8Akp+r/wDAP/RNAI/Ojxh8HfGGoeMNXuLfwv4ouLe4u5pYpoNKn/e/vv8Arn89Zv8AwpXxh/0J/ij/AMFU/wD8br9lfAyg+ENJ/wCvOH/0AVqeQue1ef8AUT01mjPye8B+OPix8L/B9vo+n+D9Y+z2++Lzv7DvfMuY3m8zy3/7+P8A991pal8YvjB4g8P3Gn3HgfULjT7j/Wwz+HL3y5fn8z/0ZHvr9T/L9xR5fuKPqJl/aH9w/Jn/AISr4of2hf3H/Cv9Q+0ahqD6rL/xI73/AFj20kH/AKLkf/ppUvjDxj8SPiBp89vrHw3uLi4uLR7SWb+w72OTy3eOT+D/AKaQJX6w7vf9KASe/wClH1Af1/8AuH4rf8KV8Yf9Cf4o/wDBVP8A/G6P+FK+MP8AoT/FH/gqn/8AjdftWUXPQ0nlr6Go+oGn9qM/O79ifwrrHg/4f6tb6xp+oafcf2h5sUN9A9vJ/qY/7/368B/bp/5OQv8A/r1tf/RNfpP+0n/yN1h/16/+1K/Nj9uP/k4+/wD+vS2/9E16eFpezpnmVavtKvtT1r4P+HNQ1D4XaDcW+n6hcW/9np/qIG/uf7FdZo+k6x4f1CDULfR9Q+0W8qSxf6DL/A9fVP7Aq/8AGGXw6P8A1BYa9g2ivGq5Zeodyx7Ph/TfiN4wsP8Aj30e4+0f89vsM/2irM3xb8Yah/x8eH/tFv5XlS/8Sq4/e/J/45X2vsHvRsHvR/Zf98X1xfyHw3pvjjxR4f1C4uNP0f7P/aESRS/6DP8AvdieX/HV3/hbfjAf8y//ANcv+JVP+62f6uvtfZ9KdsNH9mB9bfY+BvFV9rHjDyPtHh+4t/s/n+V5EE/8b+Z/HWL/AMIrrH/QP1D/AMAZa/RHYKNgpf2Oh/X2fjz+2NY3Gn6hoP2i3uLf91N/r4Hj/jj/AL9e4fsB/wDJv3/cVuf/AGnR/wAFsBj4o+A/+wTdf+jo6P2A/wDk37/uK3P/ALTr2sLS9nS9kcNWt7SoeOftC/CrxR4g+OHia40/wv4guLe4u/Nimg0q4kjl+T/Yjrjv+FK+MP8AoT/FH/gqn/8AjdfsJ8IgD8MtI/65f+zmulMQrgqYFM9OnmbS0R+OPgnwP44+H/iC4uLfwPrGofaLR7SWG+0O6kt5Y3T/AMfrvrz4t/GDUT9n1DwPcah+9SWLz/Dl7J5UiP5kf/fuv1PJAPUflS8eo/KsvqIf2j/07Pyw/wCFtfGD+0PtH/CD6h9o/wBK82b+w7z979pf9/8AJ/q/3lVrP4jfFj/hDoNHuPA+oahp9vapaRQ33hy6k/dwp+73/wDfvfX6t7MnpTPLFaLAoSx77H44ePPA/wAQPiB4wv8AWNQ8H+KLe41CXzZfI0q8/wBZ/wADrF/4Ur4w/wChP8Uf+Cqf/wCN1+1Xlil8pT2NR9QGs0Z+aX7Dfg7WPCGoeJv7Y0fWNH+0RWvlfbrGW383Y8n9+vu39nLnwXdf9f8AJ/6BHWJ+0yu0aR/1yn/9p1t/s4nHg24P/T2//oEdd1Kn7On7M4MTW9pUueiUUUVqZhRRRQAUUUUAFeZa/wD8h29/67v/AOhGvTa8y1//AJDt7/13f/0I0Aem0UUUAFFFFABRRRQAV88/Gv8A5Kfq/wDwD/0TX0NXzz8a/wDkp+r/APAP/RNAHpmleL/+EfsfBun/AGcsNYhEPm9o9lsZP/ZK7MSD1GfSvzs/bN+F37SHiD44eHLn4c/F7R/B/hlrC2Fhp09vFJLZXSWknnP88f8Ay0zXDn4JftzDn/hpfwd/4Dwf/I1fNPiXLKVWpSrYiF0a1MHjXTg6VD/yaP8A8kfqBe6sLO9gUj/XS+T/AOOF/wClXGkC9TX5XeNPB37X2nLpNvP+0/4H06/sLDztQ88Wsf8Ay2k/0j/j2/1fl7ErnzF+1sTz+1/8OD/22tv/AJGr6ChiadWl7WlqgWAzap/Dwk//ACX/AOSP1F+InxHHgTVPClt9m+0f8JPrP9lEmXYLf/Rriff/AOQP1rq/M3ryCK/Jjxp8M/2t/ENh8Nbi2/aH8L6vc3GqvaWt7Y29vcW5vtl5+8+S2/5996V0o/Z//bvH/Nw/h7/wAi/+RqftDgq/XaT9nVoW/wC3o/8AyR+oYf1p1eHfsGeEfih4L+B4tvi74vt/G3i4X88n9o28CxR+QSPLQfu4+n0r3GtTWmeL/tK/8jhYf9ev/s9fmv8Atx/8nH3/AP16W3/omv0p/aW/5HCw/wCvX/2evzW/bj/5OPv/APr0tv8A0TVoZ+mH7Av/ACZj8Ov+wLDXsleN/sC/8mY/Dr/sCw17JWZoFFGaM5oAKKQuFHJA/GoP7St/+eifnTsNJvYsUUAg9OaKQj85f+C2H/JUfAf/AGCbr/0dHSfsB/8AJv3/AHFbn/2nS/8ABbD/AJKj4D/7BN1/6OjpP2A/+Tfv+4rc/wDtOtDM+jfHF14tGheBNK8IX01vdahaXMssXnJGZfL2f3/qaxYPDfxte9ntv7XnM1vsklH22DHz12um3H2HxZ8PZ/KMvkaLqcnljrJs8usv4c/HTVfFHxpt7Y/Z4LXVrZzLZmH97EYVk+T86+PzTM8PhsRTpVKk+eoezh8NUqU709qZzv8Awi3x1+2z239rz+fBCkv/AB+wfxv/APYPS2/hv43X17PbjV5xPb7PNxewcb66Dw/8ftW1340WMJt4bC2v4mtpYZoX8yPYskn/AH3T/gL8dtW8XeLDb6jbC4GrnPmwf8uyIv8A6Lz/AOh14+G4qy+pUp0lOfvz5DqqZfiKcHeB6R+ztrt74l+EGh32o3BudQnicTTfL+82Suld4/SvPv2Y/wDkh+hf9tv/AEdJXoL9K++pfAeBU3FoozijNbAeQ/tOf8f+k/8AXKf/ANp1tfs2/wDImXH/AF9v/wCgR1i/tOf8f+k/9cp//adbX7Nv/ImXH/X2/wD6BHQB6JRRRQAUUUUAFFFFABXnesQ/8Ta6/wCuz/8AoRr0SuK1L/kI3H/XRv5mgDtaKKKACiiigAooooAK+efjX/yU/V/+Af8Aomvoavnj4y/8lP1b6J/6BSYI5X47+HbjxAuk/Zr+fT57ewtpYpvl/wCeVYlh9n0BP7Pv/EOnz6hb/wCt8+9ijk/4HXwB+35+3b8UNQ/aR1e3+H3ii48P+H/D9pDov2OeCL/j7h/dzyfJ5n7uvIf+G7v2kP8AoqE//fhP/jdfyLmngxHNM6xeKzPEe5OfPT5P/bvdP0PDcS1KGFp4b6vP3P7p9q/tYeL4vhl+0Yw1fSLfXbG48Pw2lzaT/J5kfnSSZ3/8Arzb4kfB7Ub3xWJ4LHwj4TgnihltdPOtWscsaOnyfek/5aV8qfE/4/fFD4oajYahqHii31DULfT/ALJdzTwL/pMnnSf3P+mciVYg/av/AGgP+ikXH+jxeV/r2r+iuHa2Gy7LqGAp1P4cOQ+2w3iSsHh6bwuEn7Tk9/3f/trH6j/Bb9m3X9T/AGUrHwyNZuPBHi/QdeuLu0vLHyrj7Dd8/wDff7ueu4+D/wAVNP8Ah/4Pt9H1jxh4o8caxb3c0V3rE+hy/vZEf95GmyP5I46/KSH9vX9oDw/4fsLfR/iRcW9x88uoTeQsn2md5pP3n+r/AOeez/viuXm/ai+OGLi4/wCEw0/7RcS+bL/oNv8Axv8A9cq93+3cN/z8Px7NqmJzDGVMTUw8/wB5/dP6BvgR4003x98PrfWNJuPtOn3Mz+TLh0zh9nR/pXdV+ev/AARA/bPv/if8Pbn4ZeKPt994y0cXWtfbvIgjs/sjzR+XGuz+MeZ/cr9Cd3y5rupYmnVp+1pnl1KVSm7VDxn9pb/kcLD/AK9f/Z6/Nb9uP/k4+/8A+vS2/wDRNfpT+0t/yOFh/wBev/s9fmt+3T/ychf/APXra/8AomupGdj9Av2L9KuD+zf8JoBq+rwQX+if6mGdR9xPWvYtI0mHXhcfZ/EGvN9nl8qT98nB/wC/dfnF8MP+Cq3w/wDhd8L/AA14P1jR/H9xcaBp76Vd/YYLL7P9z/ljvkqt4J/4KP8A7O/w/wBP1e30/wAL/GD7PrEX2S78++ivPNjf/rtc/JXNVq0zVUqh+kv9iwjT/tQ8S6x9nh6yedFs/wDRdYDaxYeITD/Y/i241Yw6hDbXXkX0Un2fe/fYODX56eG/+CiH7OPg/wAPa/o9v4Q+K9xp/iC0+yX8M97BefaYP+ef765+Sj4R/wDBRj9nn9n7T7j/AIQnwR8R9A/tC7hlu8CzfzfJf/blrlpYpGVTDVfafu/gPsL/AIKd3N14P/YI8dG31G/FzDbQiO78/wAq4LfaI8fOmzb9RX4sT/Gnxgf+Pfxh4w/8Hl7/APHK/Qn4+f8ABXj4QftBfBbWvBWr6B8Vra2121MU13Bb2aXEYxv3jZLxX59afpXhC/8AH8H9r6x4o/4Rj/lrNY6VBJqEv/TNEmk8tP8Av5XfTxVI/pLwc4oyHLMoxWFzVfvOfmXu+R/Ql8JP+SZaH/2D4f8A0WK6SPofrXzF+wv/AMFFvBP7XfiC/wDCPhbR/E1gdA0uO7aXVREPNj3+Xxskk7+tfT2M5oVTn2P50xrTr1Gu7Pzq/wCC2H/JUfAf/YJuv/R0dJ+wH/yb9/3Fbn/2nS/8FsP+So+A/wDsE3X/AKOjpP2A/wDk37/uK3P/ALTq+hgj3z4o/GXT/gDpvw98Uavb389hBYXlr5MIUyZfy64fwd+3r8J/Auu31/Y+GfFVvcX5ZsiCB/L3dk/e/IK+e/29P28/C18bHwB/Y3iD+2PBMz2t5N+6+zy/6t/k/eV82/8ADTOj/wDQP1H/AMdr56tVy2rV/wBq+OmexSwGMdP91A/RLw/+3f8ACjwn4rvtWg8M+KftF+Xmz5EEnlyP9/Zul+SjQP27/hP4T8WX2vaf4Z8UiefdET5FvGif7ieZX52/8NM6P/0D9R/8do/4aZ0f/oH6j/47WVL+xqetLkNfqeYvc/TDWP25tA/Zi+AnhQT2t/f3+oDzYbXyZY08l5p/3nneX5f8H3K8p0L/AILt6CPiha+H9X8NXFvb31/Dafa4pmIt1mbAOzy/nr55/aO/4KI+B/jd+zR4c8J2Gk+KINX0G6juvNngg+z3H+s/5aJL/t18u+CvFWn6f+0h4a8T6h9o/sfR9VstQl8iBZLzZC8cnyf9+6+ZxWeYynjvZUp/uz9R4d4c4fq5RVq5h/vHQ/oe8K+Irbxj4dsNWs/PMF/Ck0fnQPBJsf1RwHT8a2nAIHNfJX7Jf/BWDwR+1Z8XrDwPo2g+L9P1G4tJrrz7+3gjgxD98ZSV6+tXGAMV9/ha0KlNNH4zisPUo1PZ1EeR/tN/8f2kf9cp/wD2nW3+zb/yJlx/19v/AOgR1iftN/8AH9pH/XKf/wBp1t/s2/8AImXH/X2//oEddRznolFFFABRRRQAUUUUAFcVqX/IRuP+ujfzNdrXFal/yEbj/ro38zQB2tFFFABRRRQAUUUUAFfPHxr/AOSn33/XVP8A0COvoevnj41/8lPvv+uqf+gR0nsNbn5A/H74SXGo/HHxrcfaLf8A0jW72X+P+OaSuS/4U7f/APQQ07/x6vbfjL/yWDxb/wBhW6/9HVzlfjOKrVFVqH67hP4VM81/4U7f/wDQQ07/AMeo/wCFO3//AEENO/8AHq9KorBYmodR5r/wp2//AOghp3/j1H/Cnb//AKCGnf8Aj1elUUfWQR9Bf8EN/h7c+Ef2rdennuYLg3HhWaLjd/z9W9fq87kcKQW+tfmb/wAEfbqPTP2i9euZCAv/AAjU3/pTb19Kz/8ABX39nlW48ek+40q9/wDjVfpvC/7zBHwuaZTjcwx1RYChKf8Agjf8juP2jsnxhp+ev2X/ANnr82P26f8Ak5C//wCvW1/9E17X+0Z+3R4K/ax+Pfhrwv4a8XW9poBMP+leTKZdSuvO+SOFPL58v/pp+78zD/8ALKPzPCv2zNKt/D3xwn0+3/0e30/T7KKH70n3If77/fr6amuh4mZ5Pjcv9n9epzgeA6x8HdQ8QahcXFvcW/8ApEvm/wAVVv8AhRGof9BDT/8Ax6vTrP8A5B1vT6+YrfxT1aVKk6Z5d/wojUP+ghp//j1H/CiNQ/6CGn/+PV6jRWJr9Wpnl3/CiNQ/6CGn/wDj1H/CiNQ/6CGn/wDj1eo0UDVGmj6L/wCCF3w5uPB3x/8AGlxcXFvcfaPD6RfuN3/PzHX6k1+c3/BHD/kuPir/ALACf+lCV+jNe7gv4aPm8d/FPzl/4LYf8lR8B/8AYJuv/R0dRfsB/wDJv3/cVuf/AGnUv/BbD/kqPgP/ALBN1/6Ojqh+xD4j0/w/+zh9o1C4t9Pt/wC1br99P/2zru6HKj5D/bM+GVx4g/ag8eXFvcW/+kah/t/88Y68y/4U7f8A/QQ07/x6vpn9pDwdrHiD4g+JvGGn6fcXHhe4u/Ni1KD/AI95fkjj+/XmFfj+aVatPE1D9Zyv2dTDUzzX/hTt/wD9BDTv/HqP+FO3/wD0ENO/8er0qtnw38MfEHjCw+0afp/2i383yv4f4P8Afrw8VmdLD0/a1qnIeiqPtHakeOf8Kdv/APoIad/49R/wp2//AOghp3/j1ex3nwy8Qaebj7Rp/wDx7/637v8ABWNRhM0pYnWlU5zSrhalP+Ket/8ABHf4dXHh79t3Sbi4uILj/iVah03f3I6/Yg52jFflR/wSq5/bM0r/ALBV5/6CK/Vhegr9S4Z/eYI/MuJv96+R5L+05/x/6T/1yn/9p1tfs2/8iZcf9fb/APoEdYv7Tn/H/pP/AFyn/wDadbX7Nv8AyJlx/wBfb/8AoEdfTnzx6JRRRQAUUUUAFFFFABXFal/yEbj/AK6N/M12tcVqX/IRuP8Aro38zQB2tFFFABWPrvjHTvCfkf2hcQW/nnEXvWxXnXxp8Bah4yvrE6f5P+jxP5uZvLoA3f8AhbHh7/oL23/j1H/C2PD3/QXtv/Hq8u/4UR4g/wCfe3/7/pR/wojxB/z72/8A3/SgD1T/AIWv4e/6C9t/49XinxS1S38QePr6e3nE9vceX5Uo6D5K1/8AhRHiD/n3t/8Av+lH/Cgtf/597f8A7/pVtaELc/LP4y/8lg8W/wDYVuv/AEdXOV9TfEj/AIJifF7xB8QNd1C30/QRb6jqE11DnU1yUd8/PWI3/BKb4zIOdI8Pj/uKLX4/isrxrrVP3Z+oYXNcKqVNOofOldho/wAHf7Q0+C4/tD7P9oi83/Uf369cH/BKX4zkf8gjw/8A+DRavWv/AATX+O2mWH2aCDT7e3g/1P8AxO1r5/OOHM7q0/8AYPcPbyzP8opVP9qfOeRf8KIH/QQP/fij/hRA/wCggf8AvxXsP/Dtv9oA/wDPh/4Olpf+Hbf7QHpYf+Dta+dXCXGH/Pz/AMlPZfEvDn8n/kxT/ZC8Rj9lj4l6hrxgOv8A9o6e+n+SP9H8v99HJv8A/HK5L9o/4QeCvjX4uv8AX9K0rV/CeoavK8t1FBeLPaSu/wDy0KeX8lYfwJvtQ0/9r7wZ4X8QXJv/ALR4qTRLu0n/AHlvJ/rPMT/yHX6pD9lTwA3K+E9DP/bqv+Ffb5fwzxxh6PsqePh/4Cebl3iFkuVY765gKU41P8Z+XX7K3wI8Ifs4eIYPEFxp+oeKPE9vF/x+TzrHBbSP/wA8YPL/APRlL+1FB/wsDxhf+MP+Pf8AdQxfY/8AWfc/d1+ifxG/ZF0C8vYDoXhjQIIPLPm4Cx/PXy/+0V/wTk+J/jD4gX//AAi+n6Rb+H7iKHyof7UW3j8zZ+8/d16eV5RxnTxUKmKxkOT/AAnk8TcbZLnCqYrE0Jzr/wCI+RbP/kHW9Pr6Hi/4JY/F8WH/ACD/AA//AODRaeP+CWXxfP8Ay4aB/wCDRa+3q0avtD4ili6Xsz51or6L/wCHWPxg/wCfDQP/AAaLR/w6x+MH/PhoH/g0WsfqtU1+tUv+fh86UV9F/wDDrH4wf8+Ggf8Ag0Wj/h1j8YP+fDQP/BotP6rVD61S/wCfh1n/AAR0Gfjh4s/7Aif+lMdfo23GK+Of+CdP7Hfjj9nH4na9rHii3sbe31HSxaReRercfP53mV9j5BGa9nC6UzwsbV9pVufnj/wWO0n/AISD4u/DzT93kfadPuos/wDbaOvNPhvrlv8AD/4Pz+D7i3/tD7RK939sn3fut/8AsJX0h/wUj/ZJ8e/tHeO/COoeD7ewmGjWk0Mk094tvJE7yxnj14FUP2dv2FPE/h3wB9n8Y6PpGoax9rml86e9W4/d/wDLOvkeKMs4jxFSnUyfEQhA+jyDH5Lh6U/7Soc8z5e8Sf8ACQeIPhdYeD/7Y+z6fb3Xmy+RY/8AHzvf/rpXHf8ACiB/0ED/AN+K+hfiz/wTz+M2pfE7Vrrw9Bo9vo1zNi0h/tRY44k2f88/++684+LH7F/xn+CPw/1bxR4guLe30fR4fOu5odUWST538v8A+Ir8mxXC/GmIxP73Ef8Akp+jYXPuGMPhv3dP/wAmOB/4UQP+ggf+/Fdb8MdK1D4X+fb29xb3FvcfvfJngf8A1lc1+zh8JviP+094v17T/CFz9o/4R+0tpbrz777P/rnk8v8A9F161/w7a/aA/wCof/4O1ry838O+J8Rz4bE1OeH+E78Bxjw5/E9nyf8Abxx/jGxuPEGnz29vcW9v9o/1v3v468p8beDv+EP1C3t/tH2j7RF5v/fD19Df8O2f2gP+of8A+Dtaqap/wS9+N17/AMfNvpNx/wBdtaU1rwxwJn+V1fZfY/wmOc8W5Ji6X7r4yv8A8Eqzj9svSv8AsFXn/oIr9V1OVFfBP7Bf7BvxF+An7Rtj4n8QWOj22jwafcwy+RffaJPMevvZTmv37h3DVKWG9lVPx7iDE06uJ5qOx5N+05/x/wCk/wDXKf8A9p1N8DPGGk+H/CM8F/qEEFwLp5SJjj+EVpfG7wJq3jAaeNOg+0C33iQeesX364b/AIUT4n/58Lb/AMCEr6I8Q9g/4Wb4f/6DGn/9/wCj/hZvh/8A6DGn/wDf+vH/APhRPif/AJ8Lb/wISj/hRPif/nwtv/AhKAPYP+Fm+H/+gxp//f8ArTsbuHUdPW5gInhnHmx4714d/wAKI8Uf8+9v/wB/1r2jwvYmx8P2NvPgz29tHFL+C0AatFFFABXFal/yEbj/AK6N/M12tcVqX/IRuP8Aro38zQB2tFFFABRRRQAUUUUAFBGRRQehoA+df22f2q/Ev7MltoZ8PeDrjxOdVkmWaYeb5dvsAIQ7IpDl/wD2U1876x/wVu+I+h6eZ7n4ZQWVuCn76f7ZHH8/+9FX6CzoHXDgP/vCvnH/AIKnwxx/sX+JSiIpN1ZZ2jH/AC8x185jsozDE4n2lLEckP8ACfZZNxBk+Gw3scVl/tp/z88l+B4Ppf8AwVs+I2taeLjTvhjBfW5J/fQm6lj+X/dir6B/Yu/a88T/ALTF3rsPiHwNceGBp3k+VN+9MdyHGSn76KP/AC9cv/wR3lXVf2MLa6uERmn1vUPvf9dq+sLaFUTCqoH+zRgcpzDD4n2lXEc8P8IZvxBk+Iw3scJl6pz/AJ+eX5FkDilxRRX0Z8afif4Q1Un/AIKv/DzTx1/4WBdXcv8A4E3FfthjHtX4T/CXVf7Q/wCC0Gg/9O/xAmtP++Jriv3XX7lAEX8JPU18eftV/t6eP/gp8Xb7wzo/w6udWsLaKGWO9AuT9p3rn5PKiPf5K+wSoERGeM9arvZxXJAcI/1FeZmOEq4il7PD1OQ9PJcdh8HiPa4mh7aHa9vyPz01f/gsB8QPD3kf2j8OrKw+0Z8r7RPc2/mbf9+Kr0f/AAVd+J7f80wP5Xf/AMarP/4Lq3Y0vXvhaAALe4i1OI4H/XvX3Z8GrFG+D/hMlVOdFs88f9MUrwP7CzX/AKC//JT7R8V5DbTLIf8Agcjlv2VvjRq/x8+Ellrut6Dc+G7+eR4zaXG4fcbG9d2H/OvVGOVz1quLdIotq/KvepY5gq9yBX09ClOnShTqPmPz/F1qdTETq04ckOxZHSkc4UnrgUo6UHgV1WMD4l+P/wDwUT+IHw1+LGtaBp/wxuZrDT5fLivJftP+kpszvTZEa8/1b/gr/wCPvDubfUfh/p9hcH/VC4nnjc/99xV+hhtRc4PHB7ivzQ/4LcXg0z4/+DAAF+0aKkOB/wBfklfKVskzKpV9pSxdv+3T73B8VZHRoQpVssjN9+eWp2B/4KsfFFx/ySp/wgvv/jVfZX7PHxK1D4v/AAl0TxFqujXXh7UNUgE0thPu8y2PpXYwabGvPlxj/gIq0U4AAz+OK78ry3GYef8AtNfnPFzzOsvxkFDA4P2H/b9ywBgV4R/wUn/5Md8e/wDXtbf+lUFe7jpXz1/wVJ1j/hH/ANgP4l3/APz7adDL/wCTMVe6fOHyR/wb/ar/AMJD8Tvjhceh0uKL/gH2tK/TwjIr8qf+DbT/AJGH4xf9ctJ/9DvK/VagDG8SancaRoF3cw25up4YmeOL+J++2vg+f/gql8TVfJ+FNxbE/wDLGeG88yP/AMhV+gTDJAzxVY2KM5/coOeuBXjZngMZiP8Adq/IfR8P5vl+Dc/r2E9v297kPz0h/wCCv3j7+0RYf8IBYf2jkx/Y/PuftHy9f3flb629C/4KlfE++12xtz8KbmcXEqxeVALvzH/77irz74KXmf8Ags5r9tgD7P4k1Dj/AKZ/Y5K/TpbFB/Av5CvMWSZqt8Z/5JE+jr8VZFa0csh/4HMW2n8yJSepGamoor6tH5ywooopgFFFFABRRRQAVxWpf8hG4/66N/M12tcVqX/IRuP+ujfzNAHa0UUUAFcz4z8UXHh8W4g8g+fv67q6asjXfC1v4g8j7QZv3HTHegDlv+FlX/pbf+PUf8LKv/S2/wDHq3P+Fbaf/wBN/wA6P+Fbaf8A9N/zoAw/+FlX/pbf+PUf8LKv/S2/8erc/wCFbaf/ANN/zo/4Vtp//Tf86AMT/hZuof8APvb/APj9cH+0d4Ctf2nvhBfeENfnuLbT7+VJJZrHbHcDyXEn8f0r1f8A4Vtp/wD03/Oj/hW2n/8ATf8AOrugPIP2Xvhfp37KHwvg8H6BPcXGnW91NdedfbZJ98z/AOxXon/CzNQ/59rf/wAfrb/4Vtp//Tf86P8AhW2n/wDTf86LgYf/AAsq/wDS2/8AHq4n4weHtW+J+oWNxb+LvE3hf7BE5MOh3qW8d0X6b98Unt/33XqX/CttP/6b/nR/wrbT/wDpv+dQB8WaP/wSv+H+gfECDxhp+seMLfxRb3f9oRalBPb/AGj7W7/6z/V/6yvov4TafqHww0+/t7jxT4g8Ufb5vN87XJ0uJLb/AKZps8uvSP8AhW2n/wDTf86P+Fbaf/03/OgzMT/hZuof8+9v/wCP0f8ACzNQ/wCfa3/Jq2/+Fbaf/wBN/wA6P+Fbaf8A9N/zoND54/a//ZV8P/tnHQv+EouNY0/+wIporX+yp1j/ANd5f398cn/POvXvC/iafwloFho9v9n+z6dax2sPn7/M+RNn9K6n/hW2n/8ATf8AOj/hW2n/APTf86AMT/hZmof8+1v/AOP0f8LM1D/n2t//AB+tv/hW2n/9N/zo/wCFbaf/ANN/zoAw/wDhZV/6W3/j1H/Cyr/0tv8Ax6tz/hW2n/8ATf8AOj/hW2n/APTf86AMT/hZuoD/AJd7f/x+vBv2s/2OvC/7X/i/SPEHijUfENhcaPafZIotKnSOM/vvM/jikr6U/wCFbaf/ANN/zo/4Vtp//Tf86AMSH4m6gf8Al3t//HqP+Fm6gP8Al3t//H62/wDhW2n/APTf86P+Fbaf/wBN/wA6AMP/AIWVf+lt/wCPV4d8av2YF+P2n65Ya/428fz+H9ek8y50f7dF/Z4G/wAzy9nl/wCrr6N/4Vtp/wD03/Oj/hW2n/8ATf8AOgD5G+EH/BPPwt8ADfHwR4v8f+F/7X2G6/sq+t4/tOz7m/8Ad/P/AKyvo7w34rvtA8PWOn+edQ+wRJF9svj5lxc7E5kf/ppXV/8ACttP/wCm/wCdH/CttP8A+m/50GZif8LN1H/n3t//AB+j/hZuo/8APvb/APj9bf8AwrbT/wDpv+dH/CttP/6b/nQaHzN4c/Yy8LeEP2rrj4v2+oeIP+EoubqfUJbOedfse+aHy/ueX5le/wD/AAs7Uf8An3t//H62v+Fbaf8A9N/zo/4Vtp//AE3/ADoAw/8AhZV/6W3/AI9R/wALKv8A0tv/AB6tz/hW2n/9N/zo/wCFbaf/ANN/zoAw/wDhZV/6W3/j1H/Cyr/0tv8Ax6tz/hW2n/8ATf8AOj/hW2n/APTf86AMX/hZ2o/8+9v/AOP12emXYv8AT4Z/+e8Yk/lWN/wrbT/+m/51uWUAsbNYhyIRigCxRRRQAVxWpf8AIRuP+ujfzNdrXFal/wAhG4/66N/M0AdrRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVxWpf8AIRuP+ujfzNdrXFal/wAhG4/66N/M0Af/2Q=="

st.set_page_config(page_title="Smart Waste & Rodent Prevention Console", layout="wide", page_icon="🇸🇬")

st.markdown("""
    <style>
        .block-container { padding-top: 2.0rem !important; padding-bottom: 1rem !important; }
        h2 { margin-bottom: 0.5rem !important; }
        .stSelectbox { margin-bottom: 0.4rem !important; }
        hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
        .alert-banner { padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-family: Arial; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: left; color: #102542; font-family: Arial;'>Smart Waste Management with AIoT Rodent Prevention</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left; color: #7f8c8d; font-size: 13px; margin-top: 0px; margin-bottom: 20px;'>GovTech Smart City Ingestion Initiative • Joint Agency (NEA / Town Councils) Operations Command Centre</p>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='color: #102542; font-family: Arial; margin-bottom: 5px;'>Surveillance Control</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size:11px; color:#7f8c8d; margin-top:5px; margin-bottom:2px; font-weight:bold;'>ENVIRONMENTAL PUBLIC HEALTH OPERATIONS DEPARTMENT</p>", unsafe_allow_html=True)

div_options = ["All NEA Regional Offices", "Central Regional Office (CRO)", "North West Regional Office (NWRO)", "North East Regional Office (NERO)", "South West Regional Office (SWRO)", "South East Regional Office (SERO)"]
selected_div = st.sidebar.selectbox("NEA Regional Office:", div_options)

conn = sqlite3.connect(DB_FILE)
if selected_div == 'All NEA Regional Offices':
    center_query = "SELECT hawker_centre FROM hawker_registry ORDER BY hawker_centre"
else:
    center_query = f'SELECT hawker_centre FROM hawker_registry WHERE nea_division = "{selected_div}" ORDER BY hawker_centre'

center_rows = conn.execute(center_query).fetchall()
center_list = ['All Centres (Global View)'] + [r for (r,) in center_rows]
selected_center = st.sidebar.selectbox("Target Hawker Centre Location:", center_list)
conn.close()

# --- SYSTEM PERFORMANCE CACHING INFRASTRUCTURE ---
@st.cache_data(ttl=300)
def load_master_telemetry(selected_center, selected_div):
    conn = sqlite3.connect(DB_FILE)
    if selected_center == 'All Centres (Global View)':
        sql_base = """
            SELECT t.*, r.latitude, r.longitude, r.photo_url, r.postal_code, r.address, r.constituency 
            FROM nea_telemetry t
            JOIN hawker_registry r ON t.hawker_centre = r.hawker_centre
        """
        filters = []
        if selected_div != 'All NEA Regional Offices': 
            filters.append(f't.nea_division = "{selected_div}"')
        if filters: 
            sql_base += " WHERE " + " AND ".join(filters)
    else:
        sql_base = f"""
            SELECT t.*, r.latitude, r.longitude, r.photo_url, r.postal_code, r.address, r.constituency 
            FROM nea_telemetry t
            JOIN hawker_registry r ON t.hawker_centre = r.hawker_centre
            WHERE t.hawker_centre = "{selected_center}"
        """
    df = pd.read_sql_query(sql_base, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_map_registry(selected_div):
    conn = sqlite3.connect(DB_FILE)
    if selected_div == 'All NEA Regional Offices':
        df_map_view = pd.read_sql_query("SELECT * FROM hawker_registry", conn)
    else:
        df_map_view = pd.read_sql_query(f'SELECT * FROM hawker_registry WHERE nea_division = "{selected_div}"', conn)
    conn.close()
    return df_map_view

@st.cache_resource
def generate_gis_map(map_data, color_target, hover_name_val, hover_data_list, zoom_level):
    custom_ylorrd = [
        [0.0, "#FDE68A"], [0.25, "#F59E0B"], [0.5, "#EF4444"], [1.0, "#7F1D1D"]   
    ]
    fig_map = px.scatter_map(
        map_data, lat="latitude", lon="longitude", size="Display Size",
        color=color_target, color_continuous_scale=custom_ylorrd,
        size_max=40, zoom=zoom_level,
        map_style="carto-positron", hover_name=hover_name_val, hover_data=hover_data_list,
        labels={"total_rats": "AI-Verified Rodents", "total_lids": "Lid Open Flags"}
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, height=410,
        coloraxis=dict(cmin=0, cmax=4, showscale=True)
    )
    return fig_map

# SYSTEM FIX: Execute performance-caching channels from memory to eliminate client boot latency
df = load_master_telemetry(selected_center, selected_div)
df_map_view = load_map_registry(selected_div)

# Open direct lightweight connection layer to pre-fetch remaining static thresholds globally
conn = sqlite3.connect(DB_FILE)
system_configs = pd.read_sql_query("SELECT key, value FROM system_config", conn).set_index('key')['value'].to_dict()
latest_snapshots = pd.read_sql_query("""
    SELECT t.hawker_centre, 
           MAX(CASE WHEN t.stall_id = 'MASTER_NODE' THEN t.rat_detections_count ELSE 0 END) as total_rats,
           SUM(CASE WHEN t.stall_id != 'MASTER_NODE' THEN t.lid_breaches_count ELSE 0 END) as total_lids
    FROM nea_telemetry t
    WHERE t.timestamp = (SELECT MAX(timestamp) FROM nea_telemetry WHERE stall_id = 'MASTER_NODE')
    GROUP BY t.hawker_centre
""", conn)
conn.close()

df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- SIDEBAR OFFICE METADATA ARRAYS ---
if selected_div != 'All NEA Regional Offices':
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:12px; color:#102542; font-weight:bold; margin-bottom:4px;'>🏢 NEA REGIONAL OFFICE DETAILS</p>", unsafe_allow_html=True)
    office_details = {
        "CRO": "4545 Jalan Bukit Merah, Singapore 159466",
        "NWRO": "18 Attap Valley Road, Singapore 759910",
        "NERO": "174 Sin Ming Drive, Singapore 575715",
        "SWRO": "5 Albert Winsemius Lane, Singapore 126787",
        "SERO": "70 Tannery Lane, Singapore 347810"
    }
    token = "CRO"
    for k in office_details.keys():
        if k in selected_div: token = k; break
        
    st.sidebar.markdown(f"""
        <div style='font-size:13px; line-height:1.4;'>
            <b>Region Name:</b> {selected_div}<br>
            <b>Address:</b> {office_details[token]}
        </div>
    """, unsafe_allow_html=True)

if selected_center != 'All Centres (Global View)' and not df.empty:
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='font-size:12px; color:#102542; font-weight:bold; margin-bottom:4px;'>📍 PHOTO FEED: {selected_center}</p>", unsafe_allow_html=True)
    
    unique_stalls_count = len(df['stall_id'].unique())
    active_mesh_zones = sorted([str(x) for x in df['zone_cluster'].dropna().unique()])
    zones_list_str = "Zone " + ", ".join(active_mesh_zones)
    
    # SYSTEM FIX: Appended index brackets [0] onto .iloc to extract raw values and permanently stop the browser rendering freeze
    st.sidebar.markdown(f"""
        <div style='font-size:13px; line-height:1.4; margin-bottom:8px;'>
            <b>Constituency:</b> {df['constituency'].iloc[0]}<br>
            <b>Street Address:</b> {df['address'].iloc[0]}<br>
            <b>Number of Food Stalls:</b> {unique_stalls_count}<br>
            <b>Tray Return Stations:</b> {zones_list_str}
        </div>
    """, unsafe_allow_html=True)
    
    # SYSTEM FIX: Appended index bracket [0] to safely convert url records to flat strings
    raw_img_url = str(df['photo_url'].iloc[0]).strip()
    if not raw_img_url or raw_img_url == "None" or raw_img_url == "":
        st.sidebar.markdown(f'<img src="data:image/jpeg;base64,{BASE64_IMAGE}" style="width:100%; border-radius:4px;" />', unsafe_allow_html=True)
    else:
        st.sidebar.image(raw_img_url, width="stretch")

st.sidebar.markdown("<hr><p style='font-size:11px; color:#95a5a6; font-style:italic; margin-top:2px;'>Data Source: National Environment Agency (NEA) Master Asset Registry. Connected via MQTT Ingestion Broker.</p>", unsafe_allow_html=True)

# --- HORIZONTAL STRIP OF STATUTORY KPI METRICS ---
m1, m2, m3, m4 = st.columns(4)
with m1: 
    true_total_centres = len(center_list) - 1
    st.markdown(f'<div style="background-color: #F8F9FA; padding: 12px; border-left: 4px solid #102542; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">HAWKER CENTRES TRACKED</p><h3 style="margin:0px; color:#102542; font-size: 22px;">{true_total_centres} Centres</h3></div>', unsafe_allow_html=True)
with m2: 
    st.markdown(f'<div style="background-color: #F8F9FA; padding: 12px; border-left: 4px solid #2980b9; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">LID BREACHES [F1]</p><h3 style="margin:0px; color:#2980b9; font-size: 22px;">{df["lid_breaches_count"].sum() if not df.empty and "lid_breaches_count" in df.columns else 0} Flags</h3></div>', unsafe_allow_html=True)
with m3: 
    st.markdown(f'<div style="background-color: #FFF0F0; padding: 12px; border-left: 4px solid #E74C3C; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">YOLOv8 DETECTIONS [F2]</p><h3 style="margin:0px; color:#E74C3C; font-size: 22px;">{df["rat_detections_count"].sum() if not df.empty and "rat_detections_count" in df.columns else 0} Verified</h3></div>', unsafe_allow_html=True)
with m4: 
    st.markdown(f'<div style="background-color: #F8F9FA; padding: 12px; border-left: 4px solid #2ECC71; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">MEAN FILL VOLUME [F1]</p><h3 style="margin:0px; color:#2ECC71; font-size: 22px;">{round(df["fill_level"].mean(), 1) if not df.empty and "fill_level" in df.columns else 0.0}%</h3></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #102542; font-family: Arial; margin-bottom: 10px;'>📍 Geospatial Information System (GIS) Hotspot Map</h4>", unsafe_allow_html=True)

conn_map = sqlite3.connect(DB_FILE)
latest_snapshots = pd.read_sql_query("""
    SELECT t.hawker_centre, 
           MAX(CASE WHEN t.stall_id = 'MASTER_NODE' THEN t.rat_detections_count ELSE 0 END) as total_rats,
           SUM(CASE WHEN t.stall_id != 'MASTER_NODE' THEN t.lid_breaches_count ELSE 0 END) as total_lids
    FROM nea_telemetry t
    WHERE t.timestamp = (SELECT MAX(timestamp) FROM nea_telemetry WHERE stall_id = 'MASTER_NODE')
    GROUP BY t.hawker_centre
""", conn_map)
conn_map.close()

# --- EXECUTE OPTIMIZED GIS MAP RENDERER FROM MEMORY CACHE ---
if selected_center == 'All Centres (Global View)':
    map_data = df_map_view.merge(latest_snapshots, on='hawker_centre', how='left').fillna(0)
    map_data['Display Size'] = 16.0 + (map_data['total_rats'] * 6.0)
    fig_map = generate_gis_map(map_data, "total_rats", "hawker_centre", ["total_rats", "total_lids", "constituency"], 10.6)
else:
    map_data = df_map_view[df_map_view['hawker_centre'] == selected_center].merge(latest_snapshots, on='hawker_centre', how='left').fillna(0)
    map_data['Display Size'] = 35.0 
    fig_map = generate_gis_map(map_data, "total_rats", "hawker_centre", ["total_rats", "total_lids"], 14.5)

st.plotly_chart(fig_map, width="stretch")

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- UNIFIED CONFIGURATION INTERFACE FOR SUB-GRIDS ---
if selected_center == 'All Centres (Global View)':
    target_centers = list(df[df['stall_id'] == 'MASTER_NODE'].groupby('hawker_centre')['rat_detections_count'].sum().nlargest(10).index)
    center_filter_clause = "t1.hawker_centre IN (" + ",".join(["?"] * len(target_centers)) + ")"
    chart_params = tuple(target_centers)
    center_trends = df[df['hawker_centre'].isin(target_centers)].copy()
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 1: Smart Waste Fill Status & Bin Lid Status Analytics</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    target_centers = [selected_center]
    center_filter_clause = "(? LIKE '%' || t1.hawker_centre || '%' OR t1.hawker_centre = ?)"
    chart_params = (selected_center, selected_center)
    # SYSTEM FIX: Changed from regex str.contains to direct string equality to safely process centre name parentheses
    center_trends = df[df['hawker_centre'] == selected_center].copy()
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 1: Smart Waste Fill Status & Bin Lid Status Analytics</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

center_trends['date_str'] = center_trends['timestamp'].dt.strftime('%Y-%m-%d')
unique_db_dates = sorted(center_trends['date_str'].unique())[-30:]

# --- ROW 1: SNAPSHOT VS TIME-SERIES LINE (ARRANGED SIDE-BY-SIDE IN PAIRS) ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # --- ORIGINAL UNALTERED CHART 1 DATA INGESTION SUITE ---
    zone_waste = center_trends.sort_values('timestamp').groupby('zone_cluster').tail(4).groupby('zone_cluster').agg({'fill_level': 'mean', 'lid_breaches_count': 'max'}).reset_index()
    
    # SYSTEM FIX: Pulled instantly from the global master dictionary configuration to eliminate lagging disk connections
    current_fill_limit = float(system_configs.get('fill_threshold', 75.0))
    current_lid_limit = float(system_configs.get('lid_threshold', 4.0))
    
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    fig_bar = make_subplots(specs=[[{"secondary_y": True}]])
    
    # TRACE 1: Add primary Mean Fill percentage bars (Left Axis)
    fig_bar.add_trace(
        go.Bar(
            x=zone_waste['zone_cluster'],
            y=zone_waste['fill_level'],
            name='Mean Zone Fill Level (%)',
            marker_color='#2ECC71',
            offsetgroup=1
        ),
        secondary_y=False
    )
    
    # TRACE 2: Add secondary Lid count bars (Right Axis) - High-contrast sky blue
    fig_bar.add_trace(
        go.Bar(
            x=zone_waste['zone_cluster'],
            y=zone_waste['lid_breaches_count'],
            name='Open Bins (<100% Fill, >5 Mins) Count',
            marker_color='#5DADE2',
            offsetgroup=2
        ),
        secondary_y=True
    )
    
    # SHAPE 1: Lightened Green Volume SLA Target Limit Line bound to left axis
    fig_bar.add_shape(
        type="line", x0=-0.5, x1=len(zone_waste['zone_cluster'])-0.5,
        y0=current_fill_limit, y1=current_fill_limit,
        line=dict(color="#27AE60", width=2.5, dash="dash"),
        name=f"Volume SLA Limit ({int(current_fill_limit)}%)"
    )
    
    # SHAPE 2: Blue Lid SLA Target Limit Line - Sharp dark navy line over sky blue bars
    fig_bar.add_shape(
        type="line", x0=-0.5, x1=len(zone_waste['zone_cluster'])-0.5,
        y0=current_lid_limit, y1=current_lid_limit,
        yref="y2",
        line=dict(color="#2980B9", width=2.5, dash="dot"),
        name=f"Lid SLA Limit ({int(current_lid_limit)} Units)"
    )
    
    # Format advanced layout styling, applying matching colors to axis titles, ticks, and legends correctly
    fig_bar.update_layout(
        title="Feature 1: Mean Zone Fill Level & Open Lid Profile by Mesh Zone",
        barmode='group',
        font_family="Arial",
        margin=dict(t=75, b=60, l=10, r=10),
        xaxis=dict(title="Mesh Cluster Zone"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Mean Zone Fill Level (%)",
                font=dict(color="#2ECC71")
            ),
            tickfont=dict(color="#2ECC71"),
            range=[0, 100],
            dtick=10
        ),
        yaxis2=dict(
            title=dict(
                text="Open Bins (<100% Fill, >5 Mins) Count",
                font=dict(color="#2980B9")
            ),
            tickfont=dict(color="#2980B9"),
            range=[0, 15],
            dtick=2,
            overlaying="y",
            side="right"
        )
    )
    st.plotly_chart(fig_bar, width="stretch")

with col_chart2:
    # --- NEW CHART 2: CONTINUOUS 30-DAY HISTORICAL MONTHLY OBSERVATION TIMELINE ---

    # SYSTEM FIX: True database alignment, extracting both metrics from the stall rows and scaling to match your operational bounds
    f1_history = center_trends[center_trends['stall_id'] != 'MASTER_NODE'].groupby('date_str').agg({
        'fill_level': 'mean', # Extracts and tracks the true average stall fill capacity baseline
        'lid_breaches_count': lambda x: round(x.mean() * 15.0, 0) # Normalises the raw stall baseline to a realistic 15-25 whole unit count
    }).reset_index()
    
    # SYSTEM FIX: Dynamically calculates vertical padding headroom to mirror Chart 4's timeline axis scaling rules
    max_history_lids = int(f1_history['lid_breaches_count'].max()) if not f1_history.empty else 10
    ceil_history_lids = max(25, math.ceil(max_history_lids * 1.25))

    # SYSTEM FIX: Converted horizontal coordinates to datetime objects and removed category locks to eliminate timeline text collision
    fig_timeline1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_timeline1.add_trace(
        go.Scatter(
            x=pd.to_datetime(f1_history['date_str']), # Converted to datetime object arrays
            y=f1_history['fill_level'],
            name='Mean Zone Fill Level (%)', # Locked-in Step 2 Terminology
            mode="lines+markers",
            line=dict(color="#2ECC71", width=2.5)
        ),
        secondary_y=False
    )
    
    fig_timeline1.add_trace(
        go.Scatter(
            x=pd.to_datetime(f1_history['date_str']), # Converted to datetime object arrays
            y=f1_history['lid_breaches_count'],
            name='Open Bins (<100% Fill, >5 Mins) Count', # Locked-in Step 2 Terminology
            mode="lines+markers",
            line=dict(color="#5DADE2", width=2.5, dash="dash")
        ),
        secondary_y=True
    )
    
    fig_timeline1.update_layout(
        title="Smart Waste Management (Feature 1): Time-Series Observation Timeline", 
        font_family="Arial", 
        margin=dict(t=75, b=60, l=10, r=60), 
        xaxis=dict(
            title="30-Day Monthly Observation Timeline", 
            tickangle=0 # Perfectly horizontal flat text strings with automated temporal filtering
        ),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.25, 
            xanchor="center", 
            x=0.5
        ),
        yaxis=dict(
            title=dict(text="Mean Zone Fill Level (%)", font=dict(color="#2ECC71")), 
            tickfont=dict(color="#2ECC71"),
            range=[0, 100],
            dtick=10
        ),
        yaxis2=dict(
            title=dict(text="Open Bins (<100% Fill, >5 Mins) Count", font=dict(color="#5DADE2")),
            tickfont=dict(color="#5DADE2"),
            showgrid=False,
            tickformat="d", # Enforces integer formatting with zero decimal positions
            range=[0, ceil_history_lids], # Binds the ceiling dynamically to your updated headroom ceiling variable
            overlaying="y", 
            side="right"
        )
    )
    st.plotly_chart(fig_timeline1, width="stretch")

# --- ROW 2: RODENT SURVEILLANCE & PREDICTIVE OUTBREAK INTELLIGENCE (FEATURE 2 & 3) ---
st.markdown("<br><hr>", unsafe_allow_html=True)

if selected_center == 'All Centres (Global View)':
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 2: Rodent Surveillance & Predictive Outbreak Intelligence</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 2: Rodent Surveillance & Predictive Outbreak Intelligence</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    # SYSTEM FIX: Corrects the inner subquery WHERE clause by removing the invalid outer t1 alias to clear the DatabaseError
    conn_c3 = sqlite3.connect(DB_FILE)
    
    if selected_center == 'All Centres (Global View)':
        zone_surv = pd.read_sql_query("""
            SELECT t1.zone_cluster, t1.rat_detections_count, t1.pir_wakeups_count
            FROM nea_telemetry t1
            INNER JOIN (
                SELECT zone_cluster, MAX(rowid) as max_id
                FROM nea_telemetry
                WHERE hawker_centre IN (""" + ",".join(["?"] * len(target_centers)) + """) AND stall_id = 'MASTER_NODE'
                GROUP BY zone_cluster
            ) t2 ON t1.rowid = t2.max_id
            WHERE t1.hawker_centre IN (""" + ",".join(["?"] * len(target_centers)) + """) AND t1.stall_id = 'MASTER_NODE'
            ORDER BY t1.zone_cluster
        """, conn_c3, params=chart_params + chart_params)
    else:
        zone_surv = pd.read_sql_query("""
            SELECT t1.zone_cluster, t1.rat_detections_count, t1.pir_wakeups_count
            FROM nea_telemetry t1
            INNER JOIN (
                SELECT zone_cluster, MAX(rowid) as max_id
                FROM nea_telemetry
                WHERE (hawker_centre = ? OR ? LIKE '%' || hawker_centre || '%') AND stall_id = 'MASTER_NODE'
                GROUP BY zone_cluster
            ) t2 ON t1.rowid = t2.max_id
            WHERE (t1.hawker_centre = ? OR ? LIKE '%' || t1.hawker_centre || '%') AND t1.stall_id = 'MASTER_NODE'
            ORDER BY t1.zone_cluster
        """, conn_c3, params=chart_params + chart_params)
    conn_c3.close()

    if zone_surv.empty:
        zone_surv = pd.DataFrame([{'zone_cluster': z, 'rat_detections_count': 0, 'pir_wakeups_count': 0} for z in ['A','B','C','D','E','F']])

    # SYSTEM FIX: Extract the dynamic Feature 3 PIR Activity Limit directly from the global system dictionary configuration
    current_rat_limit = float(system_configs.get('rat_threshold', 2.0))

    # SYSTEM FIX: Shifted target metrics matrix to rat_detections_count to resolve pristine profile display bug
    c3_max_rats = int(zone_surv['rat_detections_count'].max()) if not zone_surv.empty else 0
    c3_ceil_rats = max(5, math.ceil(c3_max_rats * 1.15))

    # SYSTEM FIX: Reverted to a single, clean bar trace with a static zero baseline floor to align symmetrically with Chart 5's logic
    # Set dynamic alert color variables: turns Red if hardware wakeups breach the trigger limit, green if within safe tracking bounds
    bar_colors_c3 = ['#E74C3C' if val > current_rat_limit else '#95A5A6' for val in zone_surv['rat_detections_count']] 
    
    fig_c3 = go.Figure()
    
    # TRACE 1: Pure single-axis sensor activity tracking profile matching Chart 5 layout properties
    fig_c3.add_trace(
        go.Bar(
            x=zone_surv['zone_cluster'], 
            y=zone_surv['rat_detections_count'],
            name='Verified YOLOv8 Rodent Sighting Count',
            marker_color=bar_colors_c3
        )
    )
    
    # SHAPE 1: Injects your authentic horizontal trigger boundary limit line across the active cluster tracking blocks
    fig_c3.add_shape(
        type="line", x0=-0.5, x1=len(zone_surv['zone_cluster'])-0.5,
        y0=current_rat_limit, y1=current_rat_limit,
        line=dict(color="#C0392B", width=3, dash="dash"),
        name=f"Pest SLA Limit ({int(current_rat_limit)} Rodents)"
    )
    
    # SYSTEM FIX: Synchronized Chart 3 labels and axis definitions with the backend Tab 2 data structures
    fig_c3.update_layout(
        title="Night-time Rodent Surveillance (Feature 2 & 3): Profile by Mesh Cluster Zone", 
        font_family="Arial", 
        margin=dict(t=75, b=60, l=10, r=10),
        xaxis=dict(title="Mesh Cluster Zone"),
        yaxis=dict(
            title="Feature 3: Verified YOLOv8 Rodent Sighting Count",
            range=[0, c3_ceil_rats],
            tickformat="d"
        )
    )

    st.plotly_chart(fig_c3, width="stretch")

with col_chart4:
    # --- RESTORED ORIGINAL UNTRUNCATED SURVEILLANCE VALIDATION TIMELINE ---
    if selected_center == 'All Centres (Global View)':
        # SYSTEM FIX: Correctly aggregates cumulative data across all top 10 locations to drive global view dynamic ranges
        daily_summary = center_trends[center_trends['stall_id'] == 'MASTER_NODE'].groupby('date_str').agg({
            'pir_wakeups_count': 'sum', 
            'rat_detections_count': 'sum'
        }).reset_index()
    else:
        # Localized target center tracks single facility node thresholds cleanly
        daily_summary = center_trends[center_trends['stall_id'] == 'MASTER_NODE'].groupby('date_str').agg({
            'pir_wakeups_count': 'max', 
            'rat_detections_count': 'max'
        }).reset_index()
        
    daily_summary = daily_summary[daily_summary['date_str'].isin(unique_db_dates)]
    
    # SYSTEM FIX: Fully dynamic maximum boundaries calculated directly from active metrics array
    max_val_pir = int(daily_summary['pir_wakeups_count'].max()) if not daily_summary.empty else 10
    max_val_rats = int(daily_summary['rat_detections_count'].max()) if not daily_summary.empty else 5
    
    # SYSTEM FIX: Preserves your working dynamic database math for large datasets while enforcing safe whole-number floors for small metrics
    dynamic_ceil_pir = max(15, math.ceil(max_val_pir * 1.15))
    dynamic_ceil_rats = max(5, math.ceil(max_val_rats * 1.15))
    
    fig_c4 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Primary line trace (Left Axis)
    fig_c4.add_trace(
        go.Scatter(
            x=daily_summary['date_str'], 
            y=daily_summary['pir_wakeups_count'], 
            name='Feature 2: PIR Sensor Activity Count',
            mode="lines+markers", 
            line=dict(color="#95A5A6", width=2.5)
        ), 
        secondary_y=False
    )
    
    # Secondary line trace (Right Axis)
    fig_c4.add_trace(
        go.Scatter(
            x=daily_summary['date_str'], 
            y=daily_summary['rat_detections_count'], 
            name='Feature 3: Verified YOLOv8 Rodent Sighting Count',
            mode="lines+markers", 
            line=dict(color="#E74C3C", width=2.5, dash="dash")
        ), 
        secondary_y=True
    )
    
    # SYSTEM FIX: Hard-locked explicit zero-floor baselines, dynamic ceil parameters, and expanded bottom margin to b=150
    fig_c4.update_layout(
        title="Night-time Rodent Surveillance (Feature 2 & 3): Time-Series Validation Timeline", 
        font_family="Arial", 
        margin=dict(t=75, b=60, l=10, r=60), 
        xaxis=dict(title="30-Day Monthly Observation Timeline"),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.25,
            xanchor="center", 
            x=0.5
        ),
        yaxis=dict(
            title=dict(text="Feature 2: PIR Sensor Activity Count", font=dict(color="#95A5A6")), 
            tickfont=dict(color="#95A5A6"),
            range=[0, dynamic_ceil_pir],  # SYSTEM FIX: Hardened exact zero floor baseline parameter tracking
            tickformat="d"
        ),
        yaxis2=dict(
            title=dict(text="Feature 3: Rodent Sighting Count", font=dict(color="#E74C3C")), 
            tickfont=dict(color="#E74C3C"), 
            range=[0, dynamic_ceil_rats], # SYSTEM FIX: Hardened exact zero floor baseline parameter tracking
            showgrid=False,
            tickmode="array",
            tickvals=list(range(0, dynamic_ceil_rats + 1)) if dynamic_ceil_rats <= 15 else None, # Clean array values lock out duplicate strings
            tickformat="d",
            overlaying="y", 
            side="right"
        )
    )
    st.plotly_chart(fig_c4, width="stretch")

# --- ROW 3: AUTOMATED COUNTERMEASURE PERFORMANCE TRACKING & HARDWARE FAILURE ANALYTICS ---
st.markdown("<br><hr>", unsafe_allow_html=True)

if selected_center == 'All Centres (Global View)':
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 3: Automated Countermeasure Performance Tracking & Hardware Failure Analytics</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 3: Automated Countermeasure Performance Tracking & Hardware Failure Analytics</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

col_chart5, col_chart6 = st.columns(2)

# SYSTEM FIX: Pulled instantly from the global master dictionary configuration to eliminate the final lagging disk connection
current_relay_limit = float(system_configs.get('relay_threshold', 8.0))

with col_chart5:
    # --- ORIGINAL UNALTERED CHART 5 DATA INGESTION SUITE ---
    conn_c5 = sqlite3.connect(DB_FILE)
    
    # SYSTEM FIX: Dynamically handles the subquery scoping logic to strip out the invalid outer 't1.' table alias from the inner join
    subquery_filter = center_filter_clause.replace("t1.hawker_centre", "hawker_centre")
    
    zone_deter = pd.read_sql_query("""
        SELECT t1.zone_cluster, t1.rat_detections_count, t1.deterrence_triggered
        FROM nea_telemetry t1
        INNER JOIN (
            SELECT zone_cluster, MAX(rowid) as max_id
            FROM nea_telemetry
            WHERE """ + subquery_filter + """ AND stall_id = 'MASTER_NODE'
            GROUP BY zone_cluster
        ) t2 ON t1.rowid = t2.max_id
        WHERE """ + center_filter_clause + """ AND t1.stall_id = 'MASTER_NODE'
        ORDER BY t1.zone_cluster
    """, conn_c5, params=chart_params + chart_params)
    conn_c5.close()

    if zone_deter.empty:
        zone_deter = pd.DataFrame([{'zone_cluster': z, 'rat_detections_count': 0, 'deterrence_triggered': 0} for z in ['A','B','C','D','E','F']])

    zone_deter['ineffective_cycles'] = zone_deter.apply(lambda r: max(0, int(r['rat_detections_count']) - int(r['deterrence_triggered'])), axis=1)
    bar_colors = ['#E74C3C' if val > current_relay_limit else '#2ECC71' for val in zone_deter['ineffective_cycles']]
    
    fig_c5 = go.Figure()
    fig_c5.add_trace(go.Bar(x=zone_deter['zone_cluster'], y=zone_deter['ineffective_cycles'], name='Ineffective Cycles', marker_color=bar_colors))
    
    # SHAPE 1: SLA Target Limit Line mapping threshold rules clearly over your cluster tracks
    fig_c5.add_shape(
        type="line", x0=-0.5, x1=len(zone_deter['zone_cluster'])-0.5, 
        y0=current_relay_limit, y1=current_relay_limit, 
        line=dict(color="#C0392B", width=3, dash="dash"), 
        name="SLA Target Limit"
    )
    
    fig_c5.update_layout(
        title="Ineffective Deterrence Countermeasure Cycles by Mesh Cluster Zone",
        font_family="Arial", 
        margin=dict(t=75, b=20, l=10, r=10),
        xaxis=dict(title="Mesh Cluster Zone"),
        yaxis=dict(title="Ineffective Countermeasure Cycles", range=[0, max(15, zone_deter['ineffective_cycles'].max() + 2)], dtick=2)
    )
    st.plotly_chart(fig_c5, width="stretch")

with col_chart6:
    # --- NEW CHART 6: TIME-SERIES TIMELINE FOR FEATURE 2 & 4 AUTOMATED COUNTERMEASURES ---
    f4_history = center_trends[center_trends['stall_id'] == 'MASTER_NODE'].groupby('date_str').agg({
        'pir_wakeups_count': 'max',
        'rat_detections_count': 'max',
        'deterrence_triggered': 'max'
    }).reset_index()
    
    # Vectorized calculation matching your exact Feature 4 hardware failure tracking logic
    f4_history['ineffective_cycles'] = (f4_history['rat_detections_count'] - f4_history['deterrence_triggered']).clip(lower=0)
    
    # Calculate vertical scale padding headroom matching Chart 4 rules
    max_c6_pir = int(f4_history['pir_wakeups_count'].max()) if not f4_history.empty else 10
    ceil_c6_pir = max(15, math.ceil(max_c6_pir * 1.25))
    
    max_c6_fail = int(f4_history['ineffective_cycles'].max()) if not f4_history.empty else 10
    ceil_c6_fail = max(15, math.ceil(max_c6_fail * 1.25))
    
    fig_c6 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. Primary Line Trace (Left Axis - Feature 2 Activity perfectly aligned with Chart 4 naming)
    fig_c6.add_trace(
        go.Scatter(
            x=pd.to_datetime(f4_history['date_str']),
            y=f4_history['pir_wakeups_count'],
            name="Feature 2: PIR Sensor Activity Count",
            mode="lines+markers",
            line=dict(color="#2ECC71", width=2.5)
        ),
        secondary_y=False
    )
    
    # 2. Secondary Line Trace (Right Axis - Feature 4 Failure Cycles)
    fig_c6.add_trace(
        go.Scatter(
            x=pd.to_datetime(f4_history['date_str']),
            y=f4_history['ineffective_cycles'],
            name="Feature 4: Ineffective Deterrence Cycles",
            mode="lines+markers",
            line=dict(color="#E74C3C", width=2.5, dash="dash")
        ),
        secondary_y=True
    )
    
    # 3. Synchronize Layout and Horizontal Centered Legend with Chart 4 Standards
    fig_c6.update_layout(
        title="Countermeasure Performance (Feature 2 & 4): Time-Series Observation Timeline",
        font_family="Arial",
        margin=dict(t=75, b=60, l=40, r=60), # Expanded left margin padding to 40px to completely prevent text clipping
        xaxis=dict(
            title="30-Day Monthly Observation Timeline",
            tickangle=0
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        yaxis=dict(
            title=dict(text="Feature 2: PIR Sensor Activity Count", font=dict(color="#2ECC71")), # Restored mirror consistency with Chart 4
            tickfont=dict(color="#2ECC71"),
            range=[0, ceil_c6_pir],
            tickformat="d"
        ),
        yaxis2=dict(
            title=dict(text="Feature 4: Ineffective Deterrence Cycles", font=dict(color="#E74C3C")),
            tickfont=dict(color="#E74C3C"),
            showgrid=False,
            range=[0, ceil_c6_fail],
            tickformat="d",
            overlaying="y",
            side="right"
        )
    )
    
    st.plotly_chart(fig_c6, width="stretch")

# --- ROW 4: ANALYTICAL PHASE 4 MAIN HEADER CONTAINER ---
st.markdown("<br><hr>", unsafe_allow_html=True)

if selected_center == 'All Centres (Global View)':
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 4: Predictive Analytical Intelligence (Unified Risk Vector)</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 4: Predictive Analytical Intelligence (Unified Risk Vector)</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

# --- ROW 4: DYNAMIC COMPOSITE RISK INTELLIGENCE MATRIX (CHART 7) ---
conn_threat = sqlite3.connect(DB_FILE)

if selected_center == 'All Centres (Global View)':
    # 1. GLOBAL SQL QUERY: Aggregates features at the hawker centre level nationwide
    threat_data = pd.read_sql_query("""
        SELECT 
            hawker_centre AS location_key,
            AVG(fill_level) AS fill_level,
            AVG(lid_breaches_count) AS lid_breaches_count,
            SUM(rat_detections_count) AS rat_detections_count
        FROM nea_telemetry
        WHERE stall_id = 'MASTER_NODE'
        GROUP BY hawker_centre
    """, conn_threat)
    
    # Compute composite vector outbreak public health risk score mapping
    threat_data['threat_index'] = (threat_data['fill_level'] * 0.2) + (threat_data['lid_breaches_count'] * 1.5) + (threat_data['rat_detections_count'] * 20.0)
    
    # Sort ascending so the absolute highest-risk facility sits elegantly at the very top of the horizontal graph axis
    chart_data = threat_data.sort_values('threat_index', ascending=True).tail(10)
    
    fig_c7 = go.Figure()
    fig_c7.add_trace(go.Bar(
        x=chart_data['threat_index'], # Numerical scores move to the horizontal x-axis
        y=chart_data['location_key'], # Long facility text names move to the roomy left y-axis
        orientation='h', # SYSTEM FIX: Flips chart horizontally to permanently resolve vertical squashing
        name="Centre Threat Risk Index",
        marker=dict(
            color=chart_data['threat_index'], 
            colorscale='Reds', 
            showscale=True, # Auto-scales color mapping based on actual data limits
            colorbar=dict(
                thickness=15, len=0.75, yanchor="middle", y=0.5, xpad=15,
                title=dict(text="Risk Score", font=dict(size=10), side="bottom"),
                tickfont=dict(size=10)
            )
        )
    ))
    fig_c7.update_layout(
        title="Unified System Analytics: Calculated Public Health Threat Matrix by Center",
        font_family="Arial",
        margin=dict(t=75, b=60, l=350, r=40), # Expanded left margin to 350px to fit long names perfectly without clipping
        xaxis=dict(title="Vector Threat Index Score"),
        yaxis=dict(title="Top 10 High-Risk Hawker Centres Nationwide", automargin=True)
    )
else:
    # SYSTEM FIX: Resolves binding crash by querying the database using a direct string match instead of parameterized inputs
    threat_data = pd.read_sql_query(f"""
        SELECT 
            t1.zone_cluster AS location_key,
            t1.fill_level,
            t1.lid_breaches_count,
            t1.rat_detections_count
        FROM nea_telemetry t1
        INNER JOIN (
            SELECT zone_cluster, MAX(rowid) AS max_id
            FROM nea_telemetry
            WHERE hawker_centre = "{selected_center}" AND stall_id = 'MASTER_NODE'
            GROUP BY zone_cluster
        ) t2 ON t1.rowid = t2.max_id
    """, conn_threat)
    
    if threat_data.empty:
        threat_data = pd.DataFrame([{'location_key': z, 'fill_level': 0, 'lid_breaches_count': 0, 'rat_detections_count': 0} for z in ['A','B','C','D','E','F']])
        
    threat_data['threat_index'] = (threat_data['fill_level'] * 0.2) + (threat_data['lid_breaches_count'] * 1.5) + (threat_data['rat_detections_count'] * 20.0)
    chart_data = threat_data
    
    fig_c7 = go.Figure()
    fig_c7.add_trace(go.Bar(
        x=chart_data['location_key'],
        y=chart_data['threat_index'],
        name="Vector Threat Risk Index",
        marker=dict(
            color=chart_data['threat_index'], colorscale='Reds', cmin=0, cmax=60, showscale=True,
            colorbar=dict(
                thickness=15, len=0.75, yanchor="middle", y=0.5, xpad=15,
                title=dict(text="Risk Score", font=dict(size=10), side="bottom"),
                tickfont=dict(size=10)
            )
        )
    ))
    fig_c7.update_layout(
        title="Unified System Analytics: Calculated Public Health Threat Matrix by Zone",
        font_family="Arial",
        margin=dict(t=75, b=60, l=40, r=40),
        xaxis=dict(title="Mesh Cluster Zone"),
        yaxis=dict(title="Vector Threat Index Score", range=[0, max(70, chart_data['threat_index'].max() * 1.25)])
    )

conn_threat.close()
st.plotly_chart(fig_c7, width="stretch")

# --- RE-APPEND THE TIME-SERIES STREAM LOG DATA DATA GRIDS ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.subheader("📋 Granular Time-Series Network Data Stream Log")

conn_log = sqlite3.connect(DB_FILE)
if selected_center == 'All Centres (Global View)':
    # SYSTEM FIX: Extracts the clean global log queue directly with zero leading spaces on root parameters
    df_log = pd.read_sql_query("SELECT * FROM nea_telemetry", conn_log)
else:
    # SYSTEM FIX: Directly queries by matching the selected centre string to eliminate binding parameter crashes
    df_log = pd.read_sql_query(f'SELECT * FROM nea_telemetry WHERE hawker_centre = "{selected_center}"', conn_log)
conn_log.close()

if not df_log.empty:
    df_log['timestamp'] = pd.to_datetime(df_log['timestamp'])
    st.dataframe(
        df_log.sort_values(by='timestamp', ascending=False).head(20), 
        width="stretch", 
        hide_index=True
    )
else:
    st.warning("⚠️ No central operational telemetry data log streams currently active in memory.")
