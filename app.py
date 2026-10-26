import streamlit as st
import pandas as pd

st.set_page_config(page_title="Управление: Аренда Полуприцепов", layout="wide")
st.title("🎛️ Интерактивная модель поштучного планирования парка")
st.caption("Абсолютная кастомизация: индивидуальные ставки, простои, цены покупки и расходы для каждой единицы")

# ==========================================
# ЛЕВАЯ ПАНЕЛЬ УПРАВЛЕНИЯ (ГЛОБАЛЬНЫЕ ПАРАМЕТРЫ)
# ==========================================
st.sidebar.header("🛠️ 1. ГЛОБАЛЬНЫЕ ФИНАНСЫ")
capital = st.sidebar.number_input("Стартовый капитал инвестора (B10, руб.)", value=16521375, step=500000)
leasing_down_pct = st.sidebar.slider("Стартовый аванс по лизингу (доля)", 0.1, 0.5, 0.2, 0.05)
leasing_rate = st.sidebar.slider("Годовая ставка лизинга (доля)", 0.10, 0.30, 0.18, 0.01)
lease_term_contract = st.sidebar.slider("Срок договора аренды (возврат залога, мес)", 3, 24, 11, 1)

st.sidebar.header("📅 2. ГРАФИК ЗАКУПОК (МЕСЯЦЫ ЧЕРЕЗ ЗАПЯТУЮ)")
own_months_str = st.sidebar.text_input("Месяцы покупки ЗА СВОИ средства:", "1, 1, 1, 1, 1")
lease_months_str = st.sidebar.text_input("Месяцы покупки В ЛИЗИНГ:", "7, 7, 12, 12, 12")

st.sidebar.header("👥 3. ЗАРПЛАТЫ И АУТСОРСИНГ")
salary_manager_net = st.sidebar.number_input("Оклад Менеджера на руки (руб.)", value=100000, step=10000)
count_managers = st.sidebar.number_input("Количество менеджеров в штате (чел.)", value=1, min_value=0, step=1)
salary_boss_fix = st.sidebar.number_input("Базовый фикс Управляющего (СЗ, руб.)", value=50000, step=5000)
salary_boss_kpi = st.sidebar.number_input("Мотивация Управляющего за 1 прицеп (руб.)", value=20000, step=2000)
buh_cost = st.sidebar.number_input("Бухгалтерский аутсорсинг ОСНО (руб./мес.)", value=15000, step=1000)

st.sidebar.header("📊 4. НАЛОГОВЫЕ СТАВКИ (ОСНО)")
tax_nds_pct = st.sidebar.slider("Ставка НДС (доля)", 0.10, 0.25, 0.22, 0.01)
tax_profit_pct = st.sidebar.slider("Ставка Налога на прибыль (доля)", 0.15, 0.35, 0.25, 0.01)

# Парсинг месяцев закупки
def parse_months(months_str):
    if not months_str.strip(): return []
    try: return [int(m.strip()) for m in months_str.split(",") if m.strip().isdigit() and 1 <= int(m.strip()) <= 60]
    except: return []

own_birth_months = parse_months(own_months_str)
lease_birth_months = parse_months(lease_months_str)

# Формирование единого реестра закупленных машин
unit_birth_months = own_birth_months + lease_birth_months
unit_types = ["За свои"] * len(own_birth_months) + ["В лизинг"] * len(lease_birth_months)
total_planned_units = len(unit_birth_months)
# ==========================================
# ЦЕНТРАЛЬНАЯ ПАНЕЛЬ: ИНДИВИДУАЛЬНЫЕ НАСТРОЙКИ КАЖДОЙ ЕДИНИЦЫ
# ==========================================
st.header("🚛 Индивидуальная карта настроек каждого полуприцепа")
st.write("Выберите прицеп из списка, чтобы задать его персональные технические и финансовые параметры:")

# Инициализация хранилища кастомных параметров в памяти сессии
if "fleet_data" not in st.session_state or len(st.session_state.fleet_data) != total_planned_units:
    st.session_state.fleet_data = {
        f"Прицеп №{i+1}": {
            "price": 3000000, "rent": 150000, "days": 26, 
            "parking": 333, "repair": 500, "kasko": 85000, "deposit": 150000
        } for i in range(total_planned_units)
    }

if total_planned_units > 0:
    selected_unit = st.selectbox("🎯 Выберите полуприцеп для редактирования параметров:", list(st.session_state.fleet_data.keys()))
    
    # Динамические поля ввода для выбранной машины
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.fleet_data[selected_unit]["price"] = st.number_input("Цена покупки полуприцепа (руб.)", value=st.session_state.fleet_data[selected_unit]["price"], step=100000, key=f"p_{selected_unit}")
        st.session_state.fleet_data[selected_unit]["rent"] = st.number_input("Индивидуальная ставка аренды в месяц (руб.)", value=st.session_state.fleet_data[selected_unit]["rent"], step=5000, key=f"r_{selected_unit}")
        st.session_state.fleet_data[selected_unit]["deposit"] = st.number_input("Обеспечительный залог от арендатора (руб.)", value=st.session_state.fleet_data[selected_unit]["deposit"], step=10000, key=f"d_{selected_unit}")
    with col2:
        st.session_state.fleet_data[selected_unit]["days"] = st.slider("Фактические дни работы (из 30 суток)", 0, 30, st.session_state.fleet_data[selected_unit]["days"], key=f"dy_{selected_unit}")
        st.session_state.fleet_data[selected_unit]["kasko"] = st.number_input("Стоимость страхования КАСКО (годовая, руб.)", value=st.session_state.fleet_data[selected_unit]["kasko"], step=5000, key=f"k_{selected_unit}")
    with col3:
        st.session_state.fleet_data[selected_unit]["parking"] = st.number_input("Расходы на стоянку при простое (руб./день)", value=st.session_state.fleet_data[selected_unit]["parking"], step=50, key=f"pk_{selected_unit}")
        st.session_state.fleet_data[selected_unit]["repair"] = st.number_input("Расходы на ТО и ремонт при простое (руб./день)", value=st.session_state.fleet_data[selected_unit]["repair"], step=50, key=f"rp_{selected_unit}")
else:
    st.info("Укажите месяцы закупок на левой панели, чтобы сгенерировать поштучные карточки машин.")
# ==========================================
# ПОМЕСЯЧНЫЙ СКВОЗНОЙ МАТЕМАТИЧЕСКИЙ ПЕРЕСЧЕТ
# ==========================================
months_list = [f"Месяц {m}" for m in range(1, 61)]
rows = [
    "Действующий парк техники (всего ед.)", "Арендная выручка (с НДС)", "Обеспечительный залог (входящий/возвратный)",
    "Совокупный ФОТ персонала + СФР", "Выплаты Управляющему (СЗ)", "Бухгалтерский аутсорсинг", 
    "Оплата КАСКО (Квартальная)", "Переменная стоянка при простое", "Резервный ремонт и ТО", 
    "Лизинговые платежи компании", "Налог на добавленную стоимость (НДС)", "Налог на прибыль организации", 
    "Стартовые Инвестиции (Свои)", "Авансы по лизингу", "ЧИСТЫЙ КЭШ-ФЛОУ (За месяц)", "ОСТАТОК ДЕНЕГ НА СЧЕТУ ООО"
]
df_cf = pd.DataFrame(0.0, index=rows, columns=months_list)

current_balance = float(capital)
total_fot_with_sfr = (((salary_manager_net * count_managers) / (1 - 0.13))) * (1 + 0.30)
y_rev, y_tax, y_lease, y_net, y_park = [0.0]*5, [0.0]*5, [0.0]*5, [0.0]*5, [0.0]*5

r_m = leasing_rate / 12

for m in range(1, 61):
    m_lbl = f"Месяц {m}"
    active_units = sum(1 for bm in unit_birth_months if m >= bm)
    
    rev, stand, rep, kasko, deposit_flow, lease_pay, inv, adv = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    
    if total_planned_units > 0:
        for i in range(total_planned_units):
            bm = unit_birth_months[i]
            t_deal = unit_types[i]
            u_key = f"Прицеп №{i+1}"
            
            u_data = st.session_state.fleet_data[u_key]
            u_price = float(u_data["price"])
            u_rent = float(u_data["rent"])
            u_days = float(u_data["days"])
            u_parking_day = float(u_data["parking"])
            u_repair_day = float(u_data["repair"])
            u_kasko_annual = float(u_data["kasko"])
            u_deposit = float(u_data["deposit"])
            
            if m == bm:
                if t_deal == "За свои": inv += -(u_price + 300000 + 4275)
                else: adv += -(u_price * leasing_down_pct)
                    
            if m >= bm and t_deal == "В лизинг":
                u_pmt = round(u_price * (1 - leasing_down_pct) * (r_m * (1 + r_m)**60) / ((1 + r_m)**60 - 1), 0)
                lease_pay += u_pmt
                
            if m > bm:
                rev += u_rent
                stand += (30 - u_days) * u_parking_day
                rep += (30 - u_days) * u_repair_day
                if (m - bm) % 3 == 0: kasko += u_kasko_annual / 4
                    
            if m == bm + 1: deposit_flow += u_deposit
            if m == bm + 1 + int(lease_term_contract): deposit_flow -= u_deposit

    fot = float(total_fot_with_sfr) if active_units > 0 else 0.0
    sz = float(salary_boss_fix + (active_units * salary_boss_kpi)) if active_units > 0 else 0.0
    
    nds_factor = tax_nds_pct / (1 + tax_nds_pct)
    nds_total = max(0.0, (rev * nds_factor) - ((kasko + stand + rep + lease_pay) * nds_factor))
    prof_base = (rev - (rev * nds_factor)) - fot - sz - buh_cost - (kasko * (1 - nds_factor)) - (stand * (1 - nds_factor)) - (rep * (1 - nds_factor)) - (lease_pay * (1 - nds_factor))
    profit_tax = max(0.0, prof_base * tax_profit_pct)
    
    net = rev + deposit_flow - fot - sz - buh_cost - kasko - stand - rep - lease_pay - nds_total - profit_tax + inv + adv
    current_balance += net
    
    df_cf.loc[:, m_lbl] = [active_units, rev, deposit_flow, fot, sz, buh_cost, kasko, stand, rep, lease_pay, nds_total, profit_tax, inv, adv, net, current_balance]
    
    y_idx = min((m - 1) // 12, 4)
    y_rev[y_idx] += rev; y_tax[y_idx] += (nds_total + profit_tax); y_lease[y_idx] += lease_pay; y_net[y_idx] += net; y_park[y_idx] = float(active_units)

tab_cf, tab_investor = st.tabs(["📋 1. Помесячный Cash Flow (60 мес.)", "📊 2. Годовой отчет Инвестора и ROE"])

with tab_cf:
    st.subheader("📋 Помесячный расчет денежных потоков компании")
    st.dataframe(df_cf.style.format(precision=0, thousands=" "))

with tab_investor:
    st.subheader("📊 Финансовая аналитика для инвесторов")
    min_cash = df_cf.loc["ОСТАТОК ДЕНЕГ НА СЧЕТУ ООО"].min()
    if min_cash < 0: st.error(f"⚠️ КАССОВЫЙ РАЗРЫВ! Минимальный остаток: {min_cash:,.0f} руб.")
    else: st.success("✅ Оборотных средств на счете достаточно.")
    
    y_labels = ["Год 1", "Год 2", "Год 3", "Год 4", "Год 5", "Год 6"]
    df_inv = pd.DataFrame(index=["Выручка парка", "Налоги", "Лизинговые расходы", "ЧИСТЫЙ КЭШ-ФЛОУ ГОДА", "ROE %", "Стоимость парка (Инфляция 8%)"], columns=y_labels)
    dep = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
    
    u_price_avg = float(sum(u["price"] for u in st.session_state.fleet_data.values()) / total_planned_units) if total_planned_units > 0 else 3000000.0
    
    for y in range(5):
        df_inv.iloc[0, y] = f"{y_rev[y]:,.0f} руб."
        df_inv.iloc[1, y] = f"{y_tax[y]:,.0f} руб."
        df_inv.iloc[2, y] = f"{y_lease[y]:,.0f} руб."
        df_inv.iloc[3, y] = f"{y_net[y]:,.0f} руб."
        df_inv.iloc[4, y] = f"{(y_net[y] / capital) * 100:.1f}%"
        df_inv.iloc[5, y] = f"{(y_park[y] * u_price_avg * dep[y]) * (1 + 0.08)**(y + 1):,.0f} руб."
        
    df_inv.iloc[0, 5] = f"{y_rev[-1]:,.0f} руб."
    df_inv.iloc[1, 5] = f"{y_tax[-1]:,.0f} руб."
    df_inv.iloc[2, 5] = "0 руб."
    df_inv.iloc[3, 5] = f"{(y_net[-1] + y_lease[-1]):,.0f} руб."
    df_inv.iloc[4, 5] = f"{((y_net[-1] + y_lease[-1]) / capital) * 100:.1f}%"
    df_inv.iloc[5, 5] = f"{(y_park[-1] * u_price_avg * 0.4) * (1 + 0.08)**6:,.0f} руб."
    
    st.table(df_inv)
    y_net_plot = y_net + [y_net[-1] + y_lease[-1]]
    c1, c2 = st.columns(2)
    with c1: st.line_chart(df_cf.loc["ОСТАТОК ДЕНЕГ НА СЧЕТУ ООО"].astype(float))
    with c2: st.bar_chart(pd.DataFrame({"Чистый поток инвестора": y_net_plot}, index=y_labels))
