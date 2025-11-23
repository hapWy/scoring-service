import random
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.schemas.scoring import ScoringRequest, ScoringResult, ScoringStatus, ScoringConfig

class ScoringEngine:
    def __init__(self, config: ScoringConfig = None):
        self.config = config or ScoringConfig()
    
    def calculate_score(self, request: ScoringRequest) -> Dict[str, Any]:
        """Расчет скорингового балла с учетом зарплаты"""
        base_score = 500
        
        factors = {
            'loan_amount_ratio': self._calculate_amount_ratio(request.loan_amount),
            'loan_term_ratio': self._calculate_term_ratio(request.loan_term),
            'passport_risk': self._calculate_passport_risk(request.passport_number),
            'inn_risk': self._calculate_inn_risk(request.inn),
            'application_risk': self._calculate_application_risk(request.application_id),
            'income_sufficiency': self._calculate_income_sufficiency(
                request.loan_amount, 
                request.loan_term, 
                request.user_salary
            ),
            'salary_stability': self._calculate_salary_stability(request.user_salary)
        }
        
        # Применяем веса
        score = base_score
        score_details = {}
        
        for factor_name, (factor_score, factor_description) in factors.items():
            score += factor_score
            score_details[factor_name] = {
                'score': factor_score,
                'description': factor_description,
                'weight': self._get_factor_weight(factor_name)
            }
        
        # Добавляем небольшой случайный элемент
        random_factor = random.randint(-15, 15)
        score += random_factor
        score_details['random_factor'] = {
            'score': random_factor,
            'description': 'Случайная корректировка',
            'weight': 1.0
        }
        
        final_score = max(300, min(850, int(score)))
        
        return {
            'score': final_score,
            'details': score_details,
            'risk_factors': self._identify_risk_factors(factors, final_score, request.user_salary)
        }
    
    def _calculate_amount_ratio(self, amount: float) -> tuple:
        """Коэффициент на основе суммы кредита"""
        if amount <= 100000:
            return 50, "Низкая сумма кредита - минимальный риск"
        elif amount <= 500000:
            return 30, "Средняя сумма кредита - умеренный риск"
        elif amount <= 1000000:
            return 10, "Высокая сумма кредита - повышенный риск"
        else:
            return -20, "Очень высокая сумма кредита - высокий риск"
    
    def _calculate_term_ratio(self, term: int) -> tuple:
        """Коэффициент на основе срока кредита"""
        if term <= 12:
            return 40, "Короткий срок - низкий риск"
        elif term <= 36:
            return 20, "Средний срок - умеренный риск"
        else:
            return -10, "Длительный срок - повышенный риск"
    
    def _calculate_passport_risk(self, passport: str) -> tuple:
        """Оценка риска на основе паспортных данных"""
        hash_val = int(hashlib.md5(passport.encode()).hexdigest(), 16)
        risk_score = (hash_val % 41) - 20
        
        if risk_score > 10:
            return risk_score, "Паспортные данные: низкий риск"
        elif risk_score > 0:
            return risk_score, "Паспортные данные: умеренный риск"
        else:
            return risk_score, "Паспортные данные: требуется дополнительная проверка"
    
    def _calculate_inn_risk(self, inn: str) -> tuple:
        """Оценка риска на основе ИНН"""
        hash_val = int(hashlib.sha256(inn.encode()).hexdigest(), 16)
        risk_score = (hash_val % 31) - 15
        
        if risk_score > 5:
            return risk_score, "ИНН: низкий риск"
        elif risk_score > -5:
            return risk_score, "ИНН: стандартный риск"
        else:
            return risk_score, "ИНН: повышенный риск"
    
    def _calculate_application_risk(self, app_id: int) -> tuple:
        """Фактор на основе ID заявки"""
        risk_score = (app_id % 21) - 10
        
        if risk_score > 0:
            return risk_score, "Заявка: низкий риск"
        else:
            return risk_score, "Заявка: стандартный риск"
    
    def _calculate_income_sufficiency(self, amount: float, term: int, salary: Optional[float]) -> tuple:
        """Оценка достаточности дохода с учетом реальной зарплаты"""
        if not salary or salary <= 0:
            # Если зарплата не указана, используем консервативную оценку
            monthly_payment = amount / term if term > 0 else 0
            income_sufficiency_ratio = monthly_payment / 50000  # Предполагаемый средний доход
            
            if income_sufficiency_ratio < 0.3:
                return 20, "Низкая доля платежа в доходе (зарплата не указана)"
            elif income_sufficiency_ratio < 0.5:
                return 5, "Умеренная доля платежа в доходе (зарплата не указана)"
            elif income_sufficiency_ratio < 0.7:
                return -15, "Высокая доля платежа в доходе (зарплата не указана)"
            else:
                return -35, "Очень высокая доля платежа в доходе (зарплата не указана)"
        else:
            # Расчет на основе реальной зарплаты
            monthly_payment = amount / term if term > 0 else 0
            income_sufficiency_ratio = monthly_payment / float(salary)
            
            if income_sufficiency_ratio < 0.2:
                return 40, "Отличное соотношение платежа к доходу"
            elif income_sufficiency_ratio < 0.35:
                return 25, "Хорошее соотношение платежа к доходу"
            elif income_sufficiency_ratio < 0.5:
                return 10, "Удовлетворительное соотношение платежа к доходу"
            elif income_sufficiency_ratio < 0.65:
                return -10, "Повышенная доля платежа в доходе"
            else:
                return -30, "Критическая доля платежа в доходе"
    
    def _calculate_salary_stability(self, salary: Optional[float]) -> tuple:
        """Оценка стабильности дохода"""
        if not salary or salary <= 0:
            return -20, "Зарплата не указана - повышенный риск"
        elif salary < 30000:
            return -10, "Низкий уровень дохода"
        elif salary < 70000:
            return 10, "Средний уровень дохода"
        elif salary < 150000:
            return 25, "Высокий уровень дохода"
        else:
            return 35, "Очень высокий уровень дохода"
    
    def _get_factor_weight(self, factor_name: str) -> float:
        """Веса факторов"""
        weights = {
            'loan_amount_ratio': 2.0,
            'loan_term_ratio': 1.5,
            'income_sufficiency': 2.5,  # ✅ Повышенный вес для дохода
            'salary_stability': 1.8,    # ✅ Новый вес для стабильности зарплаты
            'passport_risk': 1.2,
            'inn_risk': 1.0,
            'application_risk': 0.8
        }
        return weights.get(factor_name, 1.0)
    
    def _identify_risk_factors(self, factors: Dict[str, tuple], score: int, salary: Optional[float]) -> List[Dict[str, Any]]:
        """Идентификация ключевых факторов риска"""
        risk_factors = []
        
        for factor_name, (factor_score, description) in factors.items():
            if factor_score < -10:
                risk_factors.append({
                    'factor': factor_name,
                    'severity': 'high',
                    'description': description,
                    'impact': factor_score
                })
            elif factor_score < 0:
                risk_factors.append({
                    'factor': factor_name,
                    'severity': 'medium',
                    'description': description,
                    'impact': factor_score
                })
        
        # Дополнительные риски на основе общего балла и зарплаты
        if score < 500:
            risk_factors.append({
                'factor': 'overall_score',
                'severity': 'high',
                'description': 'Общий кредитный рейтинг слишком низкий',
                'impact': -50
            })
        
        if not salary or salary <= 0:
            risk_factors.append({
                'factor': 'salary_missing',
                'severity': 'medium',
                'description': 'Зарплата не указана - невозможно оценить платежеспособность',
                'impact': -20
            })
        
        return risk_factors
    
    def evaluate_application(self, request: ScoringRequest) -> ScoringResult:
        """Полная оценка кредитной заявки с детальными причинами"""
        scoring_result = self.calculate_score(request)
        score = scoring_result['score']
        
        # Определяем статус и причины
        if score >= 750:
            status = ScoringStatus.APPROVED
            rejection_reasons = []
            approval_details = self._get_approval_details(request, score)
        elif score >= 650:
            status = ScoringStatus.APPROVED
            rejection_reasons = []
            approval_details = self._get_approval_details(request, score, limited=True)
        elif score >= 550:
            status = ScoringStatus.MANUAL_REVIEW
            rejection_reasons = self._get_rejection_reasons(scoring_result, manual_review=True)
            approval_details = None
        else:
            status = ScoringStatus.REJECTED
            rejection_reasons = self._get_rejection_reasons(scoring_result)
            approval_details = None
        
        # Формируем результат
        result = ScoringResult(
            application_id=request.application_id,
            user_id=request.user_id,
            status=status,
            score=score,
            approved_amount=approval_details['approved_amount'] if approval_details else None,
            approved_term=approval_details['approved_term'] if approval_details else None,
            interest_rate=approval_details['interest_rate'] if approval_details else None,
            monthly_payment=approval_details['monthly_payment'] if approval_details else None,
            rejection_reason="; ".join(rejection_reasons) if rejection_reasons else None,
            insurance_required=approval_details['insurance_required'] if approval_details else False,
            details={
                "calculated_score": score,
                "risk_level": self._get_risk_level(score),
                "score_details": scoring_result['details'],
                "risk_factors": scoring_result['risk_factors'],
                "rejection_reasons": rejection_reasons,
                "user_salary_used": request.user_salary if request.user_salary else "не указана",
                "decision_timestamp": datetime.utcnow().isoformat(),
                "recommendations": self._get_recommendations(scoring_result, status, request.user_salary)
            }
        )
        
        return result
    
    def _get_approval_details(self, request: ScoringRequest, score: int, limited: bool = False) -> Dict[str, Any]:
        """Детали одобренного кредита"""
        if limited:
            # Ограниченное одобрение для среднего балла
            approved_amount = min(request.loan_amount, 1000000)
            approved_term = min(request.loan_term, 36)
        else:
            approved_amount = request.loan_amount
            approved_term = request.loan_term
        
        interest_rate = self._calculate_interest_rate(score, approved_term)
        monthly_payment = self._calculate_monthly_payment(approved_amount, interest_rate, approved_term)
        
        # Страховка требуется для высоких сумм или низкого скоринга
        insurance_required = (
            approved_amount > 500000 or 
            score < 700 or 
            (request.user_salary and request.user_salary < 50000)
        )
        
        return {
            'approved_amount': approved_amount,
            'approved_term': approved_term,
            'interest_rate': interest_rate,
            'monthly_payment': monthly_payment,
            'insurance_required': insurance_required
        }
    
    def _get_rejection_reasons(self, scoring_result: Dict[str, Any], manual_review: bool = False) -> List[str]:
        """Детальные причины отказа"""
        score = scoring_result['score']
        risk_factors = scoring_result['risk_factors']
        
        reasons = []
        
        # Основные причины на основе балла
        if score < 500:
            reasons.append("Недостаточный кредитный рейтинг")
        elif score < 550:
            reasons.append("Низкий уровень кредитоспособности")
        
        # Конкретные факторы риска
        high_risk_factors = [f for f in risk_factors if f['severity'] == 'high']
        medium_risk_factors = [f for f in risk_factors if f['severity'] == 'medium']
        
        for risk_factor in high_risk_factors:
            if risk_factor['factor'] == 'income_sufficiency':
                reasons.append("Недостаточный уровень дохода для запрашиваемой суммы")
            elif risk_factor['factor'] == 'salary_missing':
                reasons.append("Не указана зарплата - невозможно оценить платежеспособность")
            elif risk_factor['factor'] == 'loan_amount_ratio':
                reasons.append("Запрашиваемая сумма превышает допустимые лимиты")
            elif risk_factor['factor'] == 'overall_score':
                reasons.append("Общий уровень риска превышает допустимые значения")
        
        for risk_factor in medium_risk_factors[:2]:  # Берем до 2 средних факторов
            if risk_factor['factor'] == 'loan_term_ratio':
                reasons.append("Запрашиваемый срок кредита несет повышенные риски")
            elif risk_factor['factor'] == 'passport_risk':
                reasons.append("Требуется дополнительная проверка паспортных данных")
            elif risk_factor['factor'] == 'salary_stability':
                reasons.append("Уровень дохода недостаточен для комфортного обслуживания кредита")
        
        # Если причины не найдены, добавляем общие
        if not reasons:
            if manual_review:
                reasons.append("Требуется ручная проверка данных заявителя")
            else:
                reasons.append("Несоответствие требованиям кредитной политики банка")
        
        return reasons
    
    def _get_recommendations(self, scoring_result: Dict[str, Any], status: ScoringStatus, user_salary: Optional[float]) -> List[str]:
        """Рекомендации для заявителя с учетом зарплаты"""
        recommendations = []
        score = scoring_result['score']
        risk_factors = scoring_result['risk_factors']
        
        if status == ScoringStatus.REJECTED:
            if score < 550:
                recommendations.append("Рекомендуем обратиться за кредитом с меньшей суммой")
                recommendations.append("Рассмотрите возможность увеличения срока кредита")
            
            if not user_salary:
                recommendations.append("Укажите вашу зарплату для более точной оценки платежеспособности")
            
            high_risk_factors = [f for f in risk_factors if f['severity'] == 'high']
            for risk_factor in high_risk_factors:
                if risk_factor['factor'] == 'income_sufficiency':
                    recommendations.append("Предоставьте документы, подтверждающие дополнительный доход")
                elif risk_factor['factor'] == 'salary_missing':
                    recommendations.append("Укажите вашу зарплату в личном кабинете")
        
        elif status == ScoringStatus.MANUAL_REVIEW:
            recommendations.append("Подготовьте дополнительные документы, подтверждающие доход")
            recommendations.append("Будьте готовы к звонку от кредитного специалиста")
            if not user_salary:
                recommendations.append("Рекомендуем указать зарплату для ускорения проверки")
        
        elif status == ScoringStatus.APPROVED:
            if scoring_result['details']['risk_level'] == 'MEDIUM':
                recommendations.append("Рассмотрите возможность страхования кредита для снижения ставки")
        
        if not recommendations:
            recommendations.append("Для уточнения деталей обратитесь в отделение банка")
        
        return recommendations
    
    def _get_risk_level(self, score: int) -> str:
        if score >= 750:
            return "LOW"
        elif score >= 650:
            return "MEDIUM"
        elif score >= 550:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _calculate_interest_rate(self, score: int, term: int) -> float:
        base_rate = self.config.base_interest_rate
        
        # Корректировка на основе скорингового балла
        if score >= 800:
            rate_adjustment = -4.0
        elif score >= 750:
            rate_adjustment = -2.5
        elif score >= 700:
            rate_adjustment = -1.5
        elif score >= 650:
            rate_adjustment = -0.5
        else:
            rate_adjustment = 1.0
        
        # Корректировка на основе срока
        if term > 36:
            term_adjustment = 1.5
        elif term > 24:
            term_adjustment = 0.5
        else:
            term_adjustment = 0.0
        
        return max(5.0, base_rate + rate_adjustment + term_adjustment)
    
    def _calculate_monthly_payment(self, amount: float, rate: float, term: int) -> float:
        monthly_rate = rate / 100 / 12
        payment = amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
        return round(payment, 2)