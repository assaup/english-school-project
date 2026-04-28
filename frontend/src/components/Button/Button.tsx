import type { ReactNode } from 'react'
import styles from './Button.module.scss'

type ButtonProps = {
    className?: string
    type?: "button" | "submit" | "reset"
    children: ReactNode
    onClick?: () => void
    isDisabled?: boolean
    variant?: 'dark' | 'light'
}

const Button = (props: ButtonProps) => {
    const {
        className = '',
        type = 'button',
        children,
        onClick,
        isDisabled,
        variant = 'dark'
    } = props

    const buttonClasses = `
        ${styles.button}
        ${variant === 'light' ? styles.button_light : ''}
        ${className}
    `.trim()

    return (
        <button
            className={buttonClasses}
            type={type}
            onClick={onClick}
            disabled={isDisabled}
        >
            {children}
        </button>
    )
}

export default Button
