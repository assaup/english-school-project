import Button from '../Button/Button'
import styles from './FormCard.module.scss'


const FormCard = () => {


    return (
        <form className={styles.form}>
            <h2 className={styles.title}>Запишитесь на бесплатный первый урок</h2>
            <label>
                <input type="text" placeholder='Имя*' required className={styles.input}/>
            </label>
            <label>
                <input type="email" placeholder='Email*' required className={styles.input}/>
            </label>
            <label>
                <input type="tel" placeholder='Телефон*' required className={styles.input}/>
            </label>
            <Button>Записаться</Button>
            <p className={styles.agreement}>
                Нажимая «Записаться», я принимаю 
                <a className={styles.link} href="#">Пользовательское соглашение</a> 
                и даю согласие на обработку своих персональных данных на условиях 
                <a className={styles.link}  href="#">Политики конфиденциальности</a>
            </p>
        </form>
    )
}

export default FormCard